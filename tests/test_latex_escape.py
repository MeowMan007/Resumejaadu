"""
tests/test_latex_escape.py

Unit tests for apps.generator.latex_utils.latex_escape().
Verifies that all LaTeX special characters are correctly escaped
so they render safely in pdflatex documents.
"""
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

from django.test import TestCase


class LaTeXEscapeTestCase(TestCase):
    """Tests for latex_escape() helper."""

    def setUp(self):
        from apps.generator.latex_utils import latex_escape
        self.escape = latex_escape

    def test_ampersand(self):
        self.assertEqual(self.escape("A & B"), r"A \& B")

    def test_percent(self):
        self.assertEqual(self.escape("50%"), r"50\%")

    def test_dollar(self):
        self.assertEqual(self.escape("$100"), r"\$100")

    def test_hash(self):
        self.assertEqual(self.escape("#1"), r"\#1")

    def test_underscore(self):
        self.assertEqual(self.escape("snake_case"), r"snake\_case")

    def test_caret(self):
        result = self.escape("x^2")
        self.assertIn("textasciicircum", result)

    def test_tilde(self):
        self.assertIn("\\textasciitilde", self.escape("~user"))

    def test_curly_braces(self):
        result = self.escape("{value}")
        self.assertIn("\\{", result)
        self.assertIn("\\}", result)

    def test_backslash(self):
        result = self.escape("a\\b")
        # backslash becomes \textbackslash{}
        self.assertIn("textbackslash", result)

    def test_empty_string(self):
        self.assertEqual(self.escape(""), "")

    def test_plain_text_unchanged(self):
        text = "Hello World"
        self.assertEqual(self.escape(text), text)

    def test_complex_string(self):
        inp = "C++ & Python; 50% faster — $100 profit!"
        result = self.escape(inp)
        # Key escapes present
        self.assertIn(r"\&", result)
        self.assertIn(r"\%", result)
        self.assertIn(r"\$", result)
        # No unescaped special chars
        self.assertNotIn(" & ", result)

    def test_none_returns_empty(self):
        """Passing None should return empty string, not raise."""
        self.assertEqual(self.escape(None), "")

    def test_url_characters(self):
        """URLs with underscores and tildes are common in resumes."""
        result = self.escape("https://github.com/user_name")
        self.assertIn(r"\_", result)
