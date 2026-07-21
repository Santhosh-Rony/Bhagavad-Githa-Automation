import os
import sys
from dotenv import load_dotenv
from logger import logger

# Load environment variables from .env file if present
load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_API_KEY_STORY = os.environ.get("GEMINI_API_KEY_STORY")
    HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
    OPENROUTER_API_KEYS = [k for k in [
        os.environ.get("OPENROUTER_API_KEY"),
        os.environ.get("OPENROUTER_FALLBACK_API_KEY"),
        os.environ.get("OPENROUTER_FALLBACK_API_KEY_1"),
        os.environ.get("OPENROUTER_FALLBACK_API_KEY_2"),
        os.environ.get("OPENROUTER_FALLBACK_API_KEY_3")
    ] if k]
    
    GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
    raw_repo = os.environ.get("GITHUB_REPOSITORY")
    GITHUB_REPOSITORY = raw_repo.split("/")[-1] if raw_repo else None
    
    INSTAGRAM_BUSINESS_ID = os.environ.get("INSTAGRAM_BUSINESS_ID")
    INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")

    # Font Configuration
    FONT_PATH = "assets/Montserrat-VariableFont_wght.ttf"
    FONT_ITALIC_PATH = "assets/Montserrat-Italic-VariableFont_wght.ttf"
    TITLE_FONT_PATH = "assets/CinzelDecorative-Bold.ttf"

    # Template Directories
    TEMPLATES_DIR = "templates"
    OUTPUT_DIR = "output"

    @classmethod
    def validate(cls):
        """Validates that all necessary environment variables are set."""
        if not cls.OPENROUTER_API_KEYS:
            logger.warning("No OpenRouter API keys found in environment variables.")
        if not cls.INSTAGRAM_ACCESS_TOKEN:
            logger.warning("INSTAGRAM_ACCESS_TOKEN missing.")
        if not cls.INSTAGRAM_BUSINESS_ID:
            logger.warning("INSTAGRAM_BUSINESS_ID missing.")
        if not cls.GITHUB_USERNAME:
            logger.warning("GITHUB_USERNAME missing.")
        if not cls.GITHUB_REPOSITORY:
            logger.warning("GITHUB_REPOSITORY missing.")

        logger.info("Configuration validated successfully.")
