"""Tests for prompt builder and template system."""

import pytest
from app.services.generation.prompt_builder import PromptBuilder, build_generation_prompt
from app.services.generation.prompt_templates import get_template, get_available_content_types


class TestPromptTemplates:
    """Test prompt template registry."""

    def test_all_content_types_have_templates(self):
        """Every supported content type should have a template."""
        expected_types = [
            "youtube_shorts",
            "youtube_longform",
            "tiktok_short",
            "blog_article",
            "x_post",
        ]
        for ct in expected_types:
            template = get_template(ct)
            assert template is not None, f"Missing template for {ct}"
            assert "system_prompt" in template
            assert "user_prompt_template" in template

    def test_get_available_content_types(self):
        types = get_available_content_types()
        assert len(types) == 5
        assert "youtube_shorts" in types
        assert "blog_article" in types

    def test_invalid_content_type_returns_none(self):
        assert get_template("invalid_type") is None


class TestPromptBuilder:
    """Test prompt building logic."""

    @pytest.fixture
    def sample_brief(self):
        return {
            "topic": "5 Tips Produktivitas Developer WFH",
            "audience": "Developer Indonesia usia 22-35",
            "objective": "Edukasi + engagement",
            "key_message": "Produktivitas bukan soal jam kerja",
            "tone": "Casual informatif",
            "language": "id",
            "references": "Referensi video Ali Abdaal",
            "target_duration": "45-60 detik",
            "target_word_count": "1500",
        }

    @pytest.fixture
    def sample_style_guides(self):
        return [
            {
                "name": "Brand Voice Guide",
                "is_active": True,
                "tone_of_voice": "Friendly, casual, tapi tetap informatif",
                "writing_rules": [
                    "Gunakan 'kamu' bukan 'Anda'",
                    "Kalimat pendek, max 20 kata",
                    "Selalu beri contoh konkret",
                ],
                "preferred_phrases": ["let's go", "yuk", "simpel banget"],
                "banned_phrases": ["selamat datang", "halo guys", "jangan lupa subscribe"],
                "brand_examples": [
                    {"text": "Tau gak sih, ternyata..."},
                    {"text": "Ini yang banyak orang salah paham..."},
                ],
                "additional_notes": "Hindari clickbait yang misleading",
            }
        ]

    @pytest.fixture
    def sample_cta_patterns(self):
        return [
            {
                "name": "Subscribe CTA",
                "is_active": True,
                "cta_text": "Kalau konten ini helpful, tap follow buat tips lainnya",
                "cta_type": "subscribe",
                "placement": "outro",
                "platform_target": "youtube",
            },
            {
                "name": "Comment CTA",
                "is_active": True,
                "cta_text": "Share di comment, kamu tim yang mana?",
                "cta_type": "comment",
                "placement": "mid",
                "platform_target": None,  # Universal
            },
        ]

    def test_build_youtube_shorts_prompt(self, sample_brief):
        """Test building YouTube Shorts prompt from brief."""
        builder = PromptBuilder(
            content_type="youtube_shorts",
            brief=sample_brief,
        )
        system_prompt = builder.build_system_prompt()
        user_prompt = builder.build_user_prompt()

        assert "YouTube Shorts" in system_prompt
        assert "5 Tips Produktivitas" in user_prompt
        assert "Developer Indonesia" in user_prompt
        assert "Bahasa Indonesia" in user_prompt
        assert "JSON" in user_prompt

    def test_build_blog_prompt(self, sample_brief):
        """Test building blog article prompt."""
        builder = PromptBuilder(
            content_type="blog_article",
            brief=sample_brief,
        )
        user_prompt = builder.build_user_prompt()

        assert "Blog" in user_prompt
        assert "article_body" in user_prompt
        assert "1500" in user_prompt

    def test_style_guide_integration(self, sample_brief, sample_style_guides):
        """Test that style guides are properly injected into prompts."""
        builder = PromptBuilder(
            content_type="youtube_shorts",
            brief=sample_brief,
            style_guides=sample_style_guides,
        )
        system_prompt = builder.build_system_prompt()
        user_prompt = builder.build_user_prompt()

        # Style guide should appear in user prompt
        assert "STYLE GUIDE" in user_prompt
        assert "Friendly, casual" in user_prompt
        assert "kamu" in user_prompt
        assert "BANNED" in user_prompt
        assert "halo guys" in user_prompt

        # Condensed rules in system prompt
        assert "JANGAN gunakan" in system_prompt

    def test_cta_pattern_integration(self, sample_brief, sample_cta_patterns):
        """Test that CTA patterns are properly injected."""
        builder = PromptBuilder(
            content_type="youtube_shorts",
            brief=sample_brief,
            cta_patterns=sample_cta_patterns,
        )
        user_prompt = builder.build_user_prompt()

        assert "CTA PATTERNS" in user_prompt
        assert "tap follow" in user_prompt
        assert "comment" in user_prompt.lower()

    def test_inactive_style_guide_excluded(self, sample_brief):
        """Inactive style guides should not appear in prompt."""
        inactive_guide = [
            {
                "name": "Old Guide",
                "is_active": False,
                "tone_of_voice": "THIS SHOULD NOT APPEAR",
                "writing_rules": None,
                "preferred_phrases": None,
                "banned_phrases": None,
                "brand_examples": None,
                "additional_notes": None,
            }
        ]
        builder = PromptBuilder(
            content_type="youtube_shorts",
            brief=sample_brief,
            style_guides=inactive_guide,
        )
        user_prompt = builder.build_user_prompt()
        assert "THIS SHOULD NOT APPEAR" not in user_prompt

    def test_invalid_content_type_raises(self, sample_brief):
        """Invalid content type should raise ValueError."""
        with pytest.raises(ValueError):
            PromptBuilder(content_type="invalid", brief=sample_brief)

    def test_convenience_function(self, sample_brief, sample_style_guides, sample_cta_patterns):
        """Test the build_generation_prompt convenience function."""
        system, user = build_generation_prompt(
            content_type="youtube_shorts",
            brief=sample_brief,
            style_guides=sample_style_guides,
            cta_patterns=sample_cta_patterns,
        )
        assert len(system) > 100
        assert len(user) > 200
        assert "5 Tips Produktivitas" in user

    def test_english_language_output(self):
        """Test English language brief."""
        brief = {
            "topic": "5 Productivity Tips for Remote Developers",
            "audience": "Tech professionals aged 25-40",
            "objective": "Educate and engage",
            "key_message": "Productivity is about systems, not hours",
            "tone": "Professional but friendly",
            "language": "en",
        }
        builder = PromptBuilder(content_type="blog_article", brief=brief)
        user_prompt = builder.build_user_prompt()
        assert "English" in user_prompt

    def test_all_content_types_build_successfully(self, sample_brief):
        """All content types should build without errors."""
        for ct in get_available_content_types():
            builder = PromptBuilder(content_type=ct, brief=sample_brief)
            system = builder.build_system_prompt()
            user = builder.build_user_prompt()
            assert len(system) > 50
            assert len(user) > 100
