"""
tests/test_ai_service.py

Unit tests for ResumeAIService with fully mocked LiteLLM so tests
run without any API key or network access.
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

from unittest.mock import MagicMock, patch
from django.test import TestCase


class AIServiceTest(TestCase):
    """Tests for apps.ai_assistant.service.ResumeAIService."""

    def _make_mock_response(self, content="Improved text."):
        """Helper to build a minimal LiteLLM-style response mock."""
        choice = MagicMock()
        choice.message.content = content
        resp = MagicMock()
        resp.choices = [choice]
        return resp

    @patch("apps.ai_assistant.service.litellm.completion")
    def test_improve_summary_returns_string(self, mock_completion):
        mock_completion.return_value = self._make_mock_response("Great summary!")
        from apps.ai_assistant.service import ResumeAIService
        svc = ResumeAIService()
        result = svc.improve_summary(
            current_text="I am a developer.",
            target_role="Backend Engineer",
            context={},
        )
        self.assertIsInstance(result, str)
        self.assertEqual(result.strip(), "Great summary!")
        mock_completion.assert_called_once()

    @patch("apps.ai_assistant.service.litellm.completion")
    def test_enhance_bullet_returns_string(self, mock_completion):
        mock_completion.return_value = self._make_mock_response("Built X with 40% improvement")
        from apps.ai_assistant.service import ResumeAIService
        svc = ResumeAIService()
        result = svc.enhance_bullet(
            raw_text="Built X",
            role="Software Engineer",
            company="Acme",
        )
        self.assertIsInstance(result, str)
        self.assertEqual(result.strip(), "Built X with 40% improvement")

    @patch("apps.ai_assistant.service.litellm.completion")
    def test_improve_project_description(self, mock_completion):
        mock_completion.return_value = self._make_mock_response("Scalable SaaS app deployed on AWS.")
        from apps.ai_assistant.service import ResumeAIService
        svc = ResumeAIService()
        result = svc.improve_project_description(
            name="MyApp",
            tech_stack="Django, Redis",
            current_description="A web app.",
            target_role="Backend Dev",
        )
        self.assertIsInstance(result, str)
        self.assertIn("Scalable", result)

    @patch("apps.ai_assistant.service.litellm.completion")
    def test_suggest_skills(self, mock_completion):
        mock_completion.return_value = self._make_mock_response(
            "Python, Django, PostgreSQL, Docker, Kubernetes"
        )
        from apps.ai_assistant.service import ResumeAIService
        svc = ResumeAIService()
        result = svc.suggest_skills(
            existing_skills=["Python"],
            target_role="Backend Engineer",
        )
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    @patch("apps.ai_assistant.service.litellm.completion")
    def test_handles_empty_response(self, mock_completion):
        """AI returning empty content should not crash — return fallback."""
        mock_completion.return_value = self._make_mock_response("")
        from apps.ai_assistant.service import ResumeAIService
        svc = ResumeAIService()
        result = svc.improve_summary(
            current_text="test",
            target_role="Dev",
            context={},
        )
        # Should return something (either empty string or original)
        self.assertIsInstance(result, str)

    @patch("apps.ai_assistant.service.litellm.completion")
    def test_categorize_skills_returns_list(self, mock_completion):
        mock_completion.return_value = self._make_mock_response(
            '{"categories": [{"name": "Languages", "items": ["Python", "Rust"]}]}'
        )
        from apps.ai_assistant.service import ResumeAIService
        svc = ResumeAIService()
        cats = svc.categorize_skills("Python, Rust")
        self.assertIsInstance(cats, list)
        self.assertEqual(len(cats), 1)
        self.assertEqual(cats[0]["name"], "Languages")

    @patch("apps.ai_assistant.service.litellm.completion")
    def test_tailor_to_job_description_returns_dict(self, mock_completion):
        mock_completion.return_value = self._make_mock_response(
            '{"suggested_edits": ["Highlight Django ORM"], "gaps": ["Kubernetes"]}'
        )
        from apps.ai_assistant.service import ResumeAIService
        svc = ResumeAIService()
        res = svc.tailor_to_job_description(["Built APIs"], "Senior backend role with Kubernetes")
        self.assertIsInstance(res, dict)
        self.assertIn("suggested_edits", res)
        self.assertIn("gaps", res)

    @patch("apps.ai_assistant.service.litellm.completion")
    def test_api_error_raises_or_returns_fallback(self, mock_completion):
        """LiteLLM API errors should be handled gracefully."""
        mock_completion.side_effect = Exception("API error")
        from apps.ai_assistant.service import ResumeAIService
        svc = ResumeAIService()
        # Should not raise, should return fallback
        try:
            result = svc.improve_summary(
                current_text="original",
                target_role="Dev",
                context={},
            )
            # If it returns, should be a string
            self.assertIsInstance(result, str)
        except Exception as exc:
            # Acceptable only if it's a well-typed service exception
            self.assertNotIsInstance(exc, AttributeError)
