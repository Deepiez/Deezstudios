"""
Prompt templates for each content type.
Each template defines:
- system_prompt: Sets the AI's role and output format
- user_prompt_template: Template that gets filled with brief data, style guide, and CTA patterns
- output_schema: Expected JSON structure from the AI response
"""

from typing import Optional


# =============================================================================
# SYSTEM PROMPTS (per content type)
# =============================================================================

SYSTEM_PROMPT_BASE = """Kamu adalah content strategist dan copywriter profesional yang ahli membuat konten berkualitas tinggi.

ATURAN PENTING:
1. Selalu output dalam format JSON yang valid sesuai schema yang diminta.
2. Jangan tambahkan teks di luar JSON.
3. Ikuti style guide yang diberikan dengan ketat.
4. Gunakan bahasa sesuai yang diminta (Indonesia atau English).
5. Pastikan setiap output actionable dan siap produksi.
6. Jangan gunakan placeholder - semua konten harus final dan bisa langsung dipakai."""

SYSTEM_PROMPT_YOUTUBE_SHORTS = SYSTEM_PROMPT_BASE + """

ROLE SPESIFIK: Kamu adalah YouTube Shorts content creator specialist.
- Shorts harus engaging dalam 3 detik pertama (hook kuat).
- Durasi script ideal: 30-60 detik.
- Format vertikal, visual-first thinking.
- CTA harus natural dan tidak memaksa."""

SYSTEM_PROMPT_YOUTUBE_LONGFORM = SYSTEM_PROMPT_BASE + """

ROLE SPESIFIK: Kamu adalah YouTube long-form content strategist.
- Video harus punya struktur yang jelas: hook, intro, body sections, conclusion.
- Retention-focused: setiap section harus punya reason to keep watching.
- SEO-aware: title dan description harus searchable.
- Script harus conversational tapi informatif."""

SYSTEM_PROMPT_TIKTOK = SYSTEM_PROMPT_BASE + """

ROLE SPESIFIK: Kamu adalah TikTok content creator specialist.
- Hook dalam 1-2 detik pertama (pattern interrupt).
- Durasi ideal: 15-60 detik.
- Trend-aware, relatable, dan shareable.
- Visual cues harus spesifik dan actionable untuk editor."""

SYSTEM_PROMPT_BLOG = SYSTEM_PROMPT_BASE + """

ROLE SPESIFIK: Kamu adalah blog content writer dan SEO specialist.
- Artikel harus well-structured dengan heading hierarchy.
- SEO-optimized: natural keyword placement.
- Readable: short paragraphs, clear language.
- Actionable: pembaca harus bisa langsung apply insights."""

SYSTEM_PROMPT_X_POST = SYSTEM_PROMPT_BASE + """

ROLE SPESIFIK: Kamu adalah X (Twitter) content strategist.
- Posts harus concise dan impactful.
- Thread structure harus logical dan engaging per tweet.
- Hook tweet harus stop-scrolling worthy.
- CTA harus subtle tapi effective."""


# =============================================================================
# USER PROMPT TEMPLATES
# =============================================================================

USER_PROMPT_YOUTUBE_SHORTS = """Buatkan konten YouTube Shorts berdasarkan brief berikut:

## BRIEF
- Topik: {topic}
- Platform: YouTube Shorts
- Audience: {audience}
- Objective: {objective}
- Key Message: {key_message}
- Tone: {tone}
- Bahasa Output: {language}
{references_section}

{style_guide_section}

{cta_section}

## OUTPUT FORMAT (JSON)
Berikan output dalam format JSON berikut:
```json
{{
  "titles": [
    "Judul opsi 1 (max 100 chars)",
    "Judul opsi 2",
    "Judul opsi 3"
  ],
  "hooks": [
    "Hook opsi 1 (kalimat pembuka yang bikin orang stop scroll)",
    "Hook opsi 2",
    "Hook opsi 3"
  ],
  "script": {{
    "hook": "Kalimat pembuka (3 detik pertama)",
    "body": "Isi utama script (25-50 detik)",
    "closing": "Penutup + transisi ke CTA (5-10 detik)"
  }},
  "description_draft": "Deskripsi video untuk YouTube (include hashtags)",
  "thumbnail_prompt": "Prompt untuk generate thumbnail image (detailed visual description)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "estimated_duration_seconds": 45,
  "visual_notes": "Catatan visual/editing untuk produksi"
}}
```"""

USER_PROMPT_YOUTUBE_LONGFORM = """Buatkan konten YouTube Long-form berdasarkan brief berikut:

## BRIEF
- Topik: {topic}
- Platform: YouTube Long-form
- Audience: {audience}
- Objective: {objective}
- Key Message: {key_message}
- Tone: {tone}
- Bahasa Output: {language}
- Target Durasi: {target_duration}
{references_section}

{style_guide_section}

{cta_section}

## OUTPUT FORMAT (JSON)
Berikan output dalam format JSON berikut:
```json
{{
  "titles": [
    "Judul opsi 1 (SEO-friendly, max 100 chars)",
    "Judul opsi 2",
    "Judul opsi 3"
  ],
  "hooks": [
    "Hook opsi 1 (30 detik pertama yang bikin orang stay)",
    "Hook opsi 2"
  ],
  "outline": [
    {{
      "section": "Hook & Intro",
      "duration_minutes": 1,
      "key_points": ["point 1", "point 2"],
      "retention_hook": "Kenapa viewer harus terus nonton"
    }},
    {{
      "section": "Section Title",
      "duration_minutes": 3,
      "key_points": ["point 1", "point 2", "point 3"],
      "retention_hook": "Teaser untuk section berikutnya"
    }}
  ],
  "full_script": "Script lengkap yang bisa langsung dibaca/dipakai recording...",
  "description_draft": "Deskripsi video lengkap dengan timestamps, links, dan hashtags",
  "thumbnail_prompt": "Prompt untuk generate thumbnail (detailed visual description)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8"],
  "estimated_duration_minutes": 10,
  "b_roll_suggestions": ["Visual suggestion 1", "Visual suggestion 2"]
}}
```"""

USER_PROMPT_TIKTOK = """Buatkan konten TikTok Short Video berdasarkan brief berikut:

## BRIEF
- Topik: {topic}
- Platform: TikTok
- Audience: {audience}
- Objective: {objective}
- Key Message: {key_message}
- Tone: {tone}
- Bahasa Output: {language}
{references_section}

{style_guide_section}

{cta_section}

## OUTPUT FORMAT (JSON)
Berikan output dalam format JSON berikut:
```json
{{
  "hooks": [
    "Hook opsi 1 (1-2 detik, pattern interrupt)",
    "Hook opsi 2",
    "Hook opsi 3"
  ],
  "script": {{
    "hook": "Opening line (1-2 detik)",
    "body": "Isi utama (15-45 detik)",
    "closing": "Penutup + CTA (3-5 detik)"
  }},
  "caption": "Caption untuk TikTok post (include hashtags)",
  "visual_cues": [
    {{
      "timestamp": "0-2s",
      "action": "Deskripsi visual/transisi/text overlay"
    }},
    {{
      "timestamp": "2-15s",
      "action": "Deskripsi visual"
    }}
  ],
  "sound_suggestion": "Saran sound/music yang cocok",
  "hashtags": ["#tag1", "#tag2", "#tag3"],
  "estimated_duration_seconds": 30,
  "trend_reference": "Trend atau format TikTok yang dipakai (jika ada)"
}}
```"""

USER_PROMPT_BLOG = """Buatkan artikel blog berdasarkan brief berikut:

## BRIEF
- Topik: {topic}
- Platform: Blog
- Audience: {audience}
- Objective: {objective}
- Key Message: {key_message}
- Tone: {tone}
- Bahasa Output: {language}
- Target Word Count: {target_word_count}
{references_section}

{style_guide_section}

{cta_section}

## OUTPUT FORMAT (JSON)
Berikan output dalam format JSON berikut:
```json
{{
  "titles": [
    "Judul opsi 1 (SEO-friendly)",
    "Judul opsi 2",
    "Judul opsi 3"
  ],
  "meta_description": "Meta description untuk SEO (max 160 chars)",
  "outline": [
    {{
      "heading": "H2 Heading",
      "subheadings": ["H3 sub 1", "H3 sub 2"],
      "key_points": ["point 1", "point 2"]
    }}
  ],
  "article_body": "Artikel lengkap dalam markdown format...",
  "cta_placement": {{
    "mid_article_cta": "CTA di tengah artikel",
    "end_article_cta": "CTA di akhir artikel"
  }},
  "internal_link_suggestions": ["Topik terkait 1", "Topik terkait 2"],
  "target_keywords": ["keyword 1", "keyword 2", "keyword 3"],
  "estimated_word_count": 1500,
  "reading_time_minutes": 7
}}
```"""

USER_PROMPT_X_POST = """Buatkan konten X (Twitter) post berdasarkan brief berikut:

## BRIEF
- Topik: {topic}
- Platform: X (Twitter)
- Audience: {audience}
- Objective: {objective}
- Key Message: {key_message}
- Tone: {tone}
- Bahasa Output: {language}
{references_section}

{style_guide_section}

{cta_section}

## OUTPUT FORMAT (JSON)
Berikan output dalam format JSON berikut:
```json
{{
  "single_posts": [
    "Post opsi 1 (max 280 chars, standalone)",
    "Post opsi 2",
    "Post opsi 3"
  ],
  "thread": [
    "Tweet 1 (hook tweet - harus bikin orang klik 'Show more')",
    "Tweet 2 (expand on the hook)",
    "Tweet 3 (main value/insight)",
    "Tweet 4 (example/proof)",
    "Tweet 5 (CTA/closing)"
  ],
  "cta_variants": [
    "CTA opsi 1",
    "CTA opsi 2"
  ],
  "hashtags": ["#tag1", "#tag2"],
  "best_posting_time": "Saran waktu posting optimal",
  "engagement_hook": "Pertanyaan atau statement untuk trigger replies"
}}
```"""


# =============================================================================
# TEMPLATE REGISTRY
# =============================================================================

PROMPT_TEMPLATES = {
    "youtube_shorts": {
        "system_prompt": SYSTEM_PROMPT_YOUTUBE_SHORTS,
        "user_prompt_template": USER_PROMPT_YOUTUBE_SHORTS,
    },
    "youtube_longform": {
        "system_prompt": SYSTEM_PROMPT_YOUTUBE_LONGFORM,
        "user_prompt_template": USER_PROMPT_YOUTUBE_LONGFORM,
    },
    "tiktok_short": {
        "system_prompt": SYSTEM_PROMPT_TIKTOK,
        "user_prompt_template": USER_PROMPT_TIKTOK,
    },
    "blog_article": {
        "system_prompt": SYSTEM_PROMPT_BLOG,
        "user_prompt_template": USER_PROMPT_BLOG,
    },
    "x_post": {
        "system_prompt": SYSTEM_PROMPT_X_POST,
        "user_prompt_template": USER_PROMPT_X_POST,
    },
}


def get_template(content_type: str) -> Optional[dict]:
    """Get prompt template for a content type."""
    return PROMPT_TEMPLATES.get(content_type)


def get_available_content_types() -> list[str]:
    """Get list of supported content types."""
    return list(PROMPT_TEMPLATES.keys())
