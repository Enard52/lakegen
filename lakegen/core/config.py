"""Configuration defaults and environment overrides for LakeGen."""

from __future__ import annotations

import os

DEFAULT_MODEL = "gpt-4o-mini"
ENV_OPENAI_MODEL = "OPENAI_MODEL"


def get_default_model() -> str:
    """Return the configured OPENAI_MODEL environment variable or default fallback."""
    return os.environ.get(ENV_OPENAI_MODEL, DEFAULT_MODEL)
