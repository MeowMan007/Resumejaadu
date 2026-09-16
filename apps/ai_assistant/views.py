"""
apps/ai_assistant/views.py — HTMX endpoints for AI enhancement.

All views:
  - Require login
  - Check rate limit before calling AI
  - Return only the enhanced textarea fragment (HTMX swap)
  - Keep original text for client-side "Undo"
"""
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .rate_limiter import check_ai_rate_limit
from .service import ai_service, AIServiceUnavailable

logger = logging.getLogger(__name__)


def _rate_limit_response():
    """Return a friendly 429 response for HTMX."""
    return HttpResponse(
        """<div class="ai-error" role="alert">
            ⚠️ You've used your AI enhancement quota for this minute.
            Please wait 60 seconds and try again.
        </div>""",
        status=429,
        content_type="text/html",
    )


def _error_response(message: str):
    return HttpResponse(
        f'<div class="ai-error" role="alert">⚠️ {message}</div>',
        status=503,
        content_type="text/html",
    )


@login_required
@require_POST
@csrf_protect
def enhance_summary(request):
    """
    POST /ai/enhance-summary/
    Body: text, target_role (optional), field_id

    Returns: <textarea> fragment with improved text (HTMX swap)
    """
    allowed, remaining = check_ai_rate_limit(request.user)
    if not allowed:
        return _rate_limit_response()

    raw_text = request.POST.get("text", "").strip()
    target_role = request.POST.get("target_role", "")
    field_id = request.POST.get("field_id", "id_summary")

    if not raw_text:
        return _error_response("Please enter some text first.")

    try:
        improved = ai_service.enhance_summary(raw_text, target_role)
        return HttpResponse(
            _textarea_fragment(field_id, improved, raw_text, remaining),
            content_type="text/html",
        )
    except AIServiceUnavailable as exc:
        return _error_response(str(exc))


@login_required
@require_POST
@csrf_protect
def enhance_bullet(request):
    """
    POST /ai/enhance-bullet/
    Body: text, role, company, field_id
    """
    allowed, remaining = check_ai_rate_limit(request.user)
    if not allowed:
        return _rate_limit_response()

    raw_text = request.POST.get("text", "").strip()
    role = request.POST.get("role", "")
    company = request.POST.get("company", "")
    field_id = request.POST.get("field_id", "")

    if not raw_text:
        return _error_response("Please enter some text first.")

    try:
        improved = ai_service.enhance_bullet(raw_text, role, company)
        return HttpResponse(
            _textarea_fragment(field_id, improved, raw_text, remaining),
            content_type="text/html",
        )
    except AIServiceUnavailable as exc:
        return _error_response(str(exc))


@login_required
@require_POST
@csrf_protect
def enhance_project(request):
    """
    POST /ai/enhance-project/
    Body: text, tech_stack, name, field_id
    """
    allowed, remaining = check_ai_rate_limit(request.user)
    if not allowed:
        return _rate_limit_response()

    raw_text = request.POST.get("text", "").strip()
    tech_stack = request.POST.get("tech_stack", "")
    name = request.POST.get("name", "")
    field_id = request.POST.get("field_id", "")

    if not raw_text:
        return _error_response("Please enter some text first.")

    try:
        improved = ai_service.enhance_project_description(raw_text, tech_stack, name)
        return HttpResponse(
            _textarea_fragment(field_id, improved, raw_text, remaining),
            content_type="text/html",
        )
    except AIServiceUnavailable as exc:
        return _error_response(str(exc))


@login_required
@require_POST
@csrf_protect
def categorize_skills(request):
    """
    POST /ai/categorize-skills/
    Body: skills (comma-separated string)

    Returns: JSON list of skill categories
    """
    allowed, remaining = check_ai_rate_limit(request.user)
    if not allowed:
        return JsonResponse({"error": "Rate limit exceeded"}, status=429)

    raw_skills = request.POST.get("skills", "").strip()
    if not raw_skills:
        return JsonResponse({"error": "No skills provided"}, status=400)

    try:
        categories = ai_service.categorize_skills(raw_skills)
        return JsonResponse({"categories": categories, "remaining": remaining})
    except AIServiceUnavailable as exc:
        return JsonResponse({"error": str(exc)}, status=503)


@login_required
@require_POST
@csrf_protect
def tailor_to_job(request):
    """
    POST /ai/tailor/
    Body: bullets (JSON array), job_description

    Returns: JSON with suggested_edits and gaps
    """
    import json

    allowed, remaining = check_ai_rate_limit(request.user)
    if not allowed:
        return JsonResponse({"error": "Rate limit exceeded"}, status=429)

    try:
        bullets = json.loads(request.POST.get("bullets", "[]"))
        job_description = request.POST.get("job_description", "").strip()
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid request data"}, status=400)

    if not bullets or not job_description:
        return JsonResponse({"error": "Bullets and job description are required"}, status=400)

    try:
        result = ai_service.tailor_to_job_description(bullets, job_description)
        result["remaining"] = remaining
        return JsonResponse(result)
    except AIServiceUnavailable as exc:
        return JsonResponse({"error": str(exc)}, status=503)


# ─── HTML Fragments ──────────────────────────────────────────────────────────

def _textarea_fragment(field_id: str, improved: str, original: str, remaining: int) -> str:
    """
    Return an HTML fragment with the improved textarea and an Undo button.
    The original text is stored in a data attribute for client-side undo.
    """
    import html
    safe_improved = html.escape(improved)
    safe_original = html.escape(original)

    return f"""
<div class="ai-result-wrapper" id="{field_id}-wrapper">
  <textarea
    id="{field_id}"
    name="{field_id.replace('id_', '')}"
    class="form-textarea w-full"
    rows="4"
    data-original="{safe_original}"
  >{safe_improved}</textarea>
  <div class="ai-actions mt-1 flex gap-2 items-center">
    <button
      type="button"
      class="btn-undo text-xs text-slate-400 hover:text-white transition"
      onclick="
        const ta = document.getElementById('{field_id}');
        ta.value = ta.dataset.original;
        this.closest('.ai-actions').querySelector('.ai-undo-notice').style.display='none';
        this.style.display='none';
      "
    >↩ Undo AI change</button>
    <span class="ai-quota text-xs text-slate-500">{remaining} AI uses left this minute</span>
  </div>
</div>
"""
