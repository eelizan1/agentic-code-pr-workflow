"""Configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME", "eelizan1/agent-task-uncompress")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-6")
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
ANTHROPIC_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "8192"))


def require_env() -> None:
    """Raise if required environment variables are missing."""
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set")
