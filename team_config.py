"""Team-facing configuration — edit this file after forking the template."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


# Team identity (required after fork)

TEAM_NAME = "SMCE OCR Product Resolver"
TEAM_MEMBERS = "Thang Nguyen"
GITHUB_REPO = "https://github.com/your-team/smce-ocr-product-resolver"
OTHER_RESOURCE = "https://example.com/project-report"
STREAMLIT_APP_URL = ""  # e.g. "https://ura-team-abc.streamlit.app" after deploy


# Streamlit page copy

SUBTITLE = "CPU-local OCR, brand extraction, and product-line resolution for private-round images"
PAGE_TITLE = f"The 2nd URA Hackathon - {TEAM_NAME}"
BROWSER_TITLE = PAGE_TITLE


# Branding assets (replace files under assets/ if needed)

ASSETS_DIR = REPO_ROOT / "assets"
FAVICON = ASSETS_DIR / "kaggle_144224_logos_thumb76_76.png"
LOGO = ASSETS_DIR / "bk_name_en.png"
LOGO_WIDTH = 280


# UI theme

THEME_PRIMARY = "#1565C0"
THEME_PRIMARY_DARK = "#0D47A1"
THEME_BG = "#FFFFFF"
THEME_TEXT = "#1A2B4A"
THEME_MUTED = "#5C6B8A"


# Default inference settings (override inside solution/pipeline.py if needed)

DEFAULT_MIN_CONF = 0.35


# Model footprint (edit when you change OCR / models — benchmark layer reads this)

MODEL_PROFILE: dict[str, str | float | None] = {
    "pipeline": "EasyOCR (vi+en) + category-neutral brand/product resolver",
    "runtime_device": "CPU",
    "product_head_mb": 0.0,
    "ocr_backend_note": "EasyOCR weights ~200 MB (downloaded once, not in repo)",
    "lightweight_notes": (
        "The resolver uses direct OCR evidence, train-label hints, source/media blocking, "
        "and a guarded unknown-brand fallback. It does not rely on fixed public-test families."
    ),
}
