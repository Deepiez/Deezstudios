"""
Prompt Builder - Assembles final prompts from brief data, style guides, and CTA patterns.
This is the core pipeline that transforms structured brief input into AI-ready prompts.
"""

from typing import Optional
from app.services.generation.prompt_templates import get_template


class PromptBuilder:
    """
    Builds complete prompts by combining:
    1. Content type template
    2. Brief data (topic, audience, objective, etc.)
    3. Style guide (tone, rules, banned phrases)
    4. CTA patterns (library of CTAs to use)
    """

    def __init__(
        self,
        content_type: str,
        brief: dict,
        style_guides: Optional[list[dict]] = None,
        cta_patterns: Optional[list[dict]] = None,
    ):
        self.content_type = content_type
        self.brief = brief
        self.style_guides = style_guides or []
        self.cta_patterns = cta_patterns or []
        self.template = get_template(content_type)

        if not self.template:
            raise ValueError(f"No template found for content type: {content_type}")

    def build_system_prompt(self) -> str:
        """Build the system prompt with style guide context."""
        system_prompt = self.template["system_prompt"]

        # Append style guide rules to system prompt if available
        if self.style_guides:
            style_context = self._build_style_context_for_system()
            if style_context:
                system_prompt += f"\n\n## STYLE RULES YANG HARUS DIIKUTI\n{style_context}"

        return system_prompt

    def build_user_prompt(self) -> str:
        """Build the user prompt by filling template with brief data."""
        template = self.template["user_prompt_template"]

        # Extract brief fields with defaults
        topic = self.brief.get("topic", "")
        audience = self.brief.get("audience", "General audience")
        objective = self.brief.get("objective", "Inform and engage")
        key_message = self.brief.get("key_message", "")
        tone = self.brief.get("tone", "Conversational")
        language = self._get_language_label()
        references = self.brief.get("references", "")
        target_duration = self.brief.get("target_duration", "8-12 menit")
        target_word_count = self.brief.get("target_word_count", "1500-2000")

        # Build optional sections
        references_section = self._build_references_section(references)
        style_guide_section = self._build_style_guide_section()
        cta_section = self._build_cta_section()

        # Fill template
        prompt = template.format(
            topic=topic,
            audience=audience,
            objective=objective,
            key_message=key_message,
            tone=tone,
            language=language,
            references_section=references_section,
            style_guide_section=style_guide_section,
            cta_section=cta_section,
            target_duration=target_duration,
            target_word_count=target_word_count,
        )

        return prompt

    def _get_language_label(self) -> str:
        """Get human-readable language label."""
        lang = self.brief.get("language", "id")
        return "Bahasa Indonesia" if lang == "id" else "English"

    def _build_references_section(self, references: str) -> str:
        """Build references section if provided."""
        if not references:
            return ""
        return f"- Referensi/Notes: {references}"

    def _build_style_guide_section(self) -> str:
        """Build style guide section from active style guides."""
        if not self.style_guides:
            return ""

        sections = ["## STYLE GUIDE"]

        for guide in self.style_guides:
            if not guide.get("is_active", True):
                continue

            sections.append(f"### {guide.get('name', 'Style Guide')}")

            tone = guide.get("tone_of_voice")
            if tone:
                sections.append(f"- Tone of Voice: {tone}")

            writing_rules = guide.get("writing_rules")
            if writing_rules:
                sections.append("- Writing Rules:")
                for rule in writing_rules:
                    sections.append(f"  - {rule}")

            preferred = guide.get("preferred_phrases")
            if preferred:
                sections.append(f"- Preferred Phrases: {', '.join(preferred)}")

            banned = guide.get("banned_phrases")
            if banned:
                sections.append(f"- BANNED Phrases (JANGAN gunakan): {', '.join(banned)}")

            examples = guide.get("brand_examples")
            if examples:
                sections.append("- Contoh Output Brand:")
                for i, example in enumerate(examples[:3], 1):
                    if isinstance(example, dict):
                        sections.append(f"  Contoh {i}: {example.get('text', str(example))}")
                    else:
                        sections.append(f"  Contoh {i}: {example}")

            notes = guide.get("additional_notes")
            if notes:
                sections.append(f"- Notes: {notes}")

        return "\n".join(sections)

    def _build_cta_section(self) -> str:
        """Build CTA section from active CTA patterns."""
        if not self.cta_patterns:
            return ""

        sections = ["## CTA PATTERNS (gunakan/adaptasi dari library ini)"]

        # Group by placement
        by_placement = {}
        for cta in self.cta_patterns:
            if not cta.get("is_active", True):
                continue
            placement = cta.get("placement", "general")
            if placement not in by_placement:
                by_placement[placement] = []
            by_placement[placement].append(cta)

        for placement, ctas in by_placement.items():
            sections.append(f"\n### {placement.title()} CTAs:")
            for cta in ctas:
                cta_text = cta.get("cta_text", "")
                cta_type = cta.get("cta_type", "")
                if cta_type:
                    sections.append(f"- [{cta_type}] {cta_text}")
                else:
                    sections.append(f"- {cta_text}")

        return "\n".join(sections)

    def _build_style_context_for_system(self) -> str:
        """Build condensed style context for system prompt."""
        rules = []
        for guide in self.style_guides:
            if not guide.get("is_active", True):
                continue
            tone = guide.get("tone_of_voice")
            if tone:
                rules.append(f"- Tone: {tone}")
            banned = guide.get("banned_phrases")
            if banned:
                rules.append(f"- JANGAN gunakan kata/frasa: {', '.join(banned[:10])}")
        return "\n".join(rules) if rules else ""


def build_generation_prompt(
    content_type: str,
    brief: dict,
    style_guides: Optional[list[dict]] = None,
    cta_patterns: Optional[list[dict]] = None,
) -> tuple[str, str]:
    """
    Convenience function to build system and user prompts.

    Returns:
        tuple: (system_prompt, user_prompt)
    """
    builder = PromptBuilder(
        content_type=content_type,
        brief=brief,
        style_guides=style_guides,
        cta_patterns=cta_patterns,
    )
    return builder.build_system_prompt(), builder.build_user_prompt()
