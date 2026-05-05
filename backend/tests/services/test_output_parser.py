"""Tests for AI output parser."""

import pytest
from app.services.generation.output_parser import OutputParser, parse_generation_output


class TestOutputParser:
    """Test JSON parsing from AI responses."""

    def test_parse_pure_json(self):
        """Parse clean JSON response."""
        raw = '{"titles": ["Title 1", "Title 2"], "hooks": ["Hook 1"], "script": {"hook": "Hi"}}'
        result, error = OutputParser.parse_json_response(raw)
        assert result is not None
        assert error is None
        assert result["titles"] == ["Title 1", "Title 2"]

    def test_parse_json_in_code_block(self):
        """Parse JSON wrapped in markdown code block."""
        raw = '''Here's the content:

```json
{
  "titles": ["Title 1", "Title 2"],
  "hooks": ["Hook 1"],
  "script": {"hook": "Opening line", "body": "Main content", "closing": "End"}
}
```

Hope this helps!'''
        result, error = OutputParser.parse_json_response(raw)
        assert result is not None
        assert error is None
        assert len(result["titles"]) == 2

    def test_parse_json_in_plain_code_block(self):
        """Parse JSON in code block without json language tag."""
        raw = '''```
{"titles": ["Title 1"], "hooks": ["Hook"]}
```'''
        result, error = OutputParser.parse_json_response(raw)
        assert result is not None
        assert result["titles"] == ["Title 1"]

    def test_parse_json_with_surrounding_text(self):
        """Parse JSON embedded in surrounding text."""
        raw = '''Based on your brief, here's the generated content:

{"titles": ["5 Tips WFH", "Rahasia Produktif"], "hooks": ["Tau gak sih..."], "script": {"hook": "a", "body": "b", "closing": "c"}}

Let me know if you need revisions.'''
        result, error = OutputParser.parse_json_response(raw)
        assert result is not None
        assert "5 Tips WFH" in result["titles"]

    def test_parse_json_with_trailing_comma(self):
        """Handle trailing commas (common AI mistake)."""
        raw = '{"titles": ["Title 1", "Title 2",], "hooks": ["Hook",]}'
        result, error = OutputParser.parse_json_response(raw)
        assert result is not None
        assert len(result["titles"]) == 2

    def test_parse_empty_response(self):
        """Empty response should return error."""
        result, error = OutputParser.parse_json_response("")
        assert result is None
        assert error is not None

    def test_parse_non_json_response(self):
        """Non-JSON response should return error."""
        raw = "I'm sorry, I cannot generate that content because..."
        result, error = OutputParser.parse_json_response(raw)
        assert result is None
        assert error is not None

    def test_parse_nested_json(self):
        """Parse deeply nested JSON structure."""
        raw = '''```json
{
  "titles": ["Title"],
  "hooks": ["Hook"],
  "script": {
    "hook": "Opening",
    "body": "This is the body with \\"quotes\\" inside",
    "closing": "End"
  },
  "visual_cues": [
    {"timestamp": "0-3s", "action": "Show text overlay"},
    {"timestamp": "3-10s", "action": "B-roll footage"}
  ],
  "tags": ["tag1", "tag2"]
}
```'''
        result, error = OutputParser.parse_json_response(raw)
        assert result is not None
        assert len(result["visual_cues"]) == 2
        assert result["visual_cues"][0]["timestamp"] == "0-3s"


class TestParseGenerationOutput:
    """Test content-type-specific output validation."""

    def test_valid_youtube_shorts_output(self):
        """Valid YouTube Shorts output should pass validation."""
        raw = '''```json
{
  "titles": ["Title 1", "Title 2"],
  "hooks": ["Hook 1", "Hook 2"],
  "script": {"hook": "Opening", "body": "Content", "closing": "End"},
  "description_draft": "Description here",
  "thumbnail_prompt": "A person looking surprised",
  "tags": ["productivity", "wfh"]
}
```'''
        result, error = parse_generation_output(raw, "youtube_shorts")
        assert result is not None
        assert error is None  # No validation warnings

    def test_missing_required_fields_youtube_shorts(self):
        """Missing required fields should produce a warning."""
        raw = '{"titles": ["Title 1"]}'  # Missing hooks and script
        result, error = parse_generation_output(raw, "youtube_shorts")
        assert result is not None  # Still returns parsed data
        assert error is not None  # But with a warning
        assert "Missing fields" in error

    def test_valid_blog_output(self):
        """Valid blog output should pass."""
        raw = '''```json
{
  "titles": ["Blog Title"],
  "meta_description": "Meta desc",
  "outline": [{"heading": "Intro", "subheadings": [], "key_points": ["point"]}],
  "article_body": "Full article content here...",
  "cta_placement": {"mid_article_cta": "CTA mid", "end_article_cta": "CTA end"}
}
```'''
        result, error = parse_generation_output(raw, "blog_article")
        assert result is not None
        assert error is None

    def test_valid_x_post_output(self):
        """Valid X post output should pass."""
        raw = '''```json
{
  "single_posts": ["Post 1", "Post 2"],
  "thread": ["Tweet 1", "Tweet 2", "Tweet 3"],
  "cta_variants": ["CTA 1"],
  "hashtags": ["#tech"]
}
```'''
        result, error = parse_generation_output(raw, "x_post")
        assert result is not None
        assert error is None

    def test_valid_tiktok_output(self):
        """Valid TikTok output should pass."""
        raw = '''```json
{
  "hooks": ["Hook 1"],
  "script": {"hook": "a", "body": "b", "closing": "c"},
  "caption": "Caption text #fyp",
  "visual_cues": [{"timestamp": "0-2s", "action": "Text overlay"}]
}
```'''
        result, error = parse_generation_output(raw, "tiktok_short")
        assert result is not None
        assert error is None
