"""
apps/ai_assistant/service.py — LiteLLM-powered AI service.

Routes to:
  - groq/llama-3.1-70b-versatile  (AI_MODEL default, free cloud tier)
  - ollama/qwen2.5:7b              (100% local, set AI_MODEL env var)
  - Any other LiteLLM-compatible endpoint

Toggle via environment:
  AI_MODEL=groq/llama-3.1-70b-versatile   GROQ_API_KEY=gsk_...
  AI_MODEL=ollama/qwen2.5:7b              (no key needed)
"""
import json
import logging
import os
import re

import litellm
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .prompts import (
    SUMMARY_SYSTEM_PROMPT, BULLET_SYSTEM_PROMPT, SKILLS_SYSTEM_PROMPT,
    TAILOR_SYSTEM_PROMPT, PROJECT_SYSTEM_PROMPT,
    build_summary_user_prompt, build_bullet_user_prompt,
    build_skills_user_prompt, build_tailor_user_prompt, build_project_user_prompt,
)

logger = logging.getLogger(__name__)

# Silence LiteLLM's noisy INFO logs
litellm.set_verbose = False


class AIServiceUnavailable(Exception):
    """Raised when the AI backend cannot be reached after retries."""


class ResumeAIService:
    """
    Unified AI service for resume enhancement operations.

    All methods accept raw user text and return improved text (or structured data).
    None of the methods will invent facts — they only improve phrasing.
    """

    MODEL: str = os.getenv("AI_MODEL", "groq/llama-3.1-70b-versatile")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")

    def __init__(self):
        # Configure Ollama base URL if using local model
        if "ollama" in self.MODEL.lower():
            os.environ["OLLAMA_API_BASE"] = self.OLLAMA_HOST

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=False,
    )
    def _run(
        self,
        system_prompt: str,
        user_text: str,
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> str:
        """
        Core LiteLLM call. Handles both Groq and Ollama transparently.

        Returns:
            The model's text response, stripped of leading/trailing whitespace.

        Raises:
            AIServiceUnavailable: after all retries exhausted
        """
        api_key = self.GROQ_API_KEY if "groq" in self.MODEL.lower() else None

        try:
            response = litellm.completion(
                model=self.MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text},
                ],
                api_key=api_key,
            )
            content = response.choices[0].message.content or ""
            return content.strip()

        except Exception as exc:
            logger.warning(f"AI call failed ({type(exc).__name__}): {exc}")
            raise

    def _parse_json_response(self, raw: str) -> dict:
        """
        Safely parse a JSON response from the model.

        Open-source models sometimes wrap JSON in markdown code fences
        (```json ... ```). This method strips them before parsing.
        """
        # Strip markdown code fences: ```json ... ``` or ``` ... ```
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw, flags=re.IGNORECASE)
        raw = raw.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse AI JSON response: {exc}\nRaw: {raw!r}")
            return {}

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────

    def enhance_summary(self, raw_text: str, target_role: str = "") -> str:
        """
        Rewrite a career summary draft into polished, resume-ready prose.

        Args:
            raw_text:    User's rough draft
            target_role: Optional target job title to focus the rewrite

        Returns:
            Improved summary string, or raw_text unchanged on failure.
        """
        if not raw_text or not raw_text.strip():
            return raw_text

        user_prompt = build_summary_user_prompt(raw_text, target_role)
        try:
            result = self._run(SUMMARY_SYSTEM_PROMPT, user_prompt, max_tokens=200)
            return result or raw_text
        except Exception as exc:
            logger.error(f"enhance_summary failed: {exc}")
            raise AIServiceUnavailable("Summary enhancement is temporarily unavailable.") from exc

    def enhance_bullet(self, raw_text: str, role: str = "", company: str = "") -> str:
        """
        Rewrite a single experience bullet point with strong action verbs and XYZ structure.

        Args:
            raw_text: The raw bullet text
            role:     Job title context
            company:  Company name context

        Returns:
            Improved bullet string, or raw_text on failure.
        """
        if not raw_text or not raw_text.strip():
            return raw_text

        user_prompt = build_bullet_user_prompt(raw_text, role, company)
        try:
            result = self._run(BULLET_SYSTEM_PROMPT, user_prompt, max_tokens=150)
            return result or raw_text
        except Exception as exc:
            logger.error(f"enhance_bullet failed: {exc}")
            raise AIServiceUnavailable("Bullet enhancement is temporarily unavailable.") from exc

    def enhance_project_description(
        self, description: str, tech_stack: str = "", name: str = ""
    ) -> str:
        """Rewrite a project description to be concise and impactful."""
        if not description or not description.strip():
            return description

        user_prompt = build_project_user_prompt(description, tech_stack, name)
        try:
            result = self._run(PROJECT_SYSTEM_PROMPT, user_prompt, max_tokens=200)
            return result or description
        except Exception as exc:
            logger.error(f"enhance_project_description failed: {exc}")
            raise AIServiceUnavailable("Project enhancement is temporarily unavailable.") from exc

    def categorize_skills(self, raw_skill_list: str) -> list[dict]:
        """
        Auto-categorize a flat list of skills into resume-ready categories.

        Args:
            raw_skill_list: Comma-separated skill string

        Returns:
            List of dicts: [{"name": "Languages", "items": ["Python", "JavaScript"]}]
        """
        if not raw_skill_list or not raw_skill_list.strip():
            return []

        user_prompt = build_skills_user_prompt(raw_skill_list)
        try:
            raw_response = self._run(
                SKILLS_SYSTEM_PROMPT, user_prompt, max_tokens=400, temperature=0.1
            )
            parsed = self._parse_json_response(raw_response)
            return parsed.get("categories", [])
        except Exception as exc:
            logger.error(f"categorize_skills failed: {exc}")
            raise AIServiceUnavailable("Skill categorization is temporarily unavailable.") from exc

    def tailor_to_job_description(
        self, bullets: list[str], job_description: str
    ) -> dict:
        """
        Suggest rewrites to align existing bullets with a job description.
        Never fabricates new skills or experience.

        Returns:
            {"suggested_edits": [...], "gaps": [...]}
        """
        if not bullets or not job_description:
            return {"suggested_edits": [], "gaps": []}

        user_prompt = build_tailor_user_prompt(bullets, job_description)
        try:
            raw_response = self._run(
                TAILOR_SYSTEM_PROMPT, user_prompt, max_tokens=800, temperature=0.2
            )
            parsed = self._parse_json_response(raw_response)
            return {
                "suggested_edits": parsed.get("suggested_edits", []),
                "gaps": parsed.get("gaps", []),
            }
        except Exception as exc:
            logger.error(f"tailor_to_job_description failed: {exc}")
            raise AIServiceUnavailable("Job tailoring is temporarily unavailable.") from exc


# Module-level singleton
ai_service = ResumeAIService()
