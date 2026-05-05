"""
Output Parser - Extracts and validates structured JSON from AI responses.
Handles various edge cases like markdown code blocks, partial JSON, etc.
"""

import json
import re
from typing import Optional


class OutputParser:
    """Parse AI response text into structured JSON data."""

    @staticmethod
    def parse_json_response(raw_text: str) -> tuple[Optional[dict], Optional[str]]:
        """
        Parse JSON from AI response text.
        Handles:
        - Pure JSON responses
        - JSON wrapped in markdown code blocks
        - JSON with surrounding text
        - Partial/malformed JSON (best effort)

        Returns:
            tuple: (parsed_dict, error_message)
        """
        if not raw_text or not raw_text.strip():
            return None, "Empty response from AI"

        text = raw_text.strip()

        # Strategy 1: Try direct JSON parse
        try:
            result = json.loads(text)
            if isinstance(result, dict):
                return result, None
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code block ```json ... ```
        json_block = OutputParser._extract_code_block(text)
        if json_block:
            try:
                result = json.loads(json_block)
                if isinstance(result, dict):
                    return result, None
            except json.JSONDecodeError:
                pass

        # Strategy 3: Find JSON object pattern in text
        json_match = OutputParser._find_json_object(text)
        if json_match:
            try:
                result = json.loads(json_match)
                if isinstance(result, dict):
                    return result, None
            except json.JSONDecodeError:
                pass

        # Strategy 4: Try to fix common JSON issues and parse
        fixed = OutputParser._fix_common_json_issues(text)
        if fixed:
            try:
                result = json.loads(fixed)
                if isinstance(result, dict):
                    return result, None
            except json.JSONDecodeError:
                pass

        # All strategies failed
        return None, f"Failed to parse JSON from AI response. Raw text length: {len(text)}"

    @staticmethod
    def _extract_code_block(text: str) -> Optional[str]:
        """Extract content from markdown code blocks."""
        # Match ```json ... ``` or ``` ... ```
        patterns = [
            r'```json\s*\n?(.*?)\n?\s*```',
            r'```\s*\n?(.*?)\n?\s*```',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _find_json_object(text: str) -> Optional[str]:
        """Find the largest JSON object in text using brace matching."""
        # Find the first { and match to its closing }
        start = text.find('{')
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape_next = False

        for i in range(start, len(text)):
            char = text[i]

            if escape_next:
                escape_next = False
                continue

            if char == '\\' and in_string:
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if in_string:
                continue

            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        return None

    @staticmethod
    def _fix_common_json_issues(text: str) -> Optional[str]:
        """Attempt to fix common JSON formatting issues."""
        # Extract potential JSON first
        json_text = OutputParser._find_json_object(text)
        if not json_text:
            # Try extracting from code block
            json_text = OutputParser._extract_code_block(text)
        if not json_text:
            json_text = text

        # Fix trailing commas before } or ]
        fixed = re.sub(r',\s*([}\]])', r'\1', json_text)

        # Fix single quotes to double quotes (risky but sometimes needed)
        # Only do this if no double quotes exist
        if '"' not in fixed and "'" in fixed:
            fixed = fixed.replace("'", '"')

        return fixed


def parse_generation_output(raw_text: str, content_type: str) -> tuple[Optional[dict], Optional[str]]:
    """
    Parse and validate generation output for a specific content type.

    Returns:
        tuple: (parsed_content_data, error_message)
    """
    parsed, error = OutputParser.parse_json_response(raw_text)

    if error:
        return None, error

    # Validate required fields based on content type
    validation_error = _validate_output_fields(parsed, content_type)
    if validation_error:
        # Return parsed data anyway but with warning
        return parsed, f"Warning: {validation_error}"

    return parsed, None


def _validate_output_fields(data: dict, content_type: str) -> Optional[str]:
    """Validate that required fields exist in parsed output."""
    required_fields = {
        "youtube_shorts": ["titles", "hooks", "script"],
        "youtube_longform": ["titles", "hooks", "outline", "full_script"],
        "tiktok_short": ["hooks", "script", "caption", "visual_cues"],
        "blog_article": ["titles", "outline", "article_body"],
        "x_post": ["single_posts", "thread"],
    }

    fields = required_fields.get(content_type, [])
    missing = [f for f in fields if f not in data]

    if missing:
        return f"Missing fields for {content_type}: {', '.join(missing)}"

    return None
