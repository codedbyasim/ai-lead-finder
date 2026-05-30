"""
Configuration Manager for AI Lead Finder System
Handles environment variables and system settings
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()


class Config:
    """Centralized configuration management"""

    def __init__(self):
        self.load_env()
        self.validate()

    def load_env(self) -> None:
        """Load all environment variables"""

        # ── Bright Data ──────────────────────────────────────────────────────
        self.BRIGHT_DATA_API_KEY      = os.getenv('BRIGHT_DATA_API_KEY', '')
        self.BRIGHT_DATA_SERP_ZONE    = os.getenv('BRIGHT_DATA_SERP_ZONE', 'serp_api2')
        self.BRIGHT_DATA_UNLOCKER_ZONE = os.getenv('BRIGHT_DATA_UNLOCKER_ZONE', 'web_unlocker1')

        # Bright Data REST API endpoint (same for SERP and Web Unlocker)
        self.BRIGHT_DATA_ENDPOINT = "https://api.brightdata.com/request"

        # ── AIML API ─────────────────────────────────────────────────────────
        self.AIML_API_KEY = os.getenv('AIML_API_KEY', '')
        self.AIML_MODEL   = os.getenv('AIML_MODEL', 'anthropic/claude-opus-4-5')
        self.AIML_BASE_URL = 'https://api.aimlapi.com/v1'

        # ── System ───────────────────────────────────────────────────────────
        self.REQUEST_TIMEOUT        = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
        self.MAX_RETRIES            = int(os.getenv('MAX_RETRIES', '3'))
        self.LOG_LEVEL              = os.getenv('LOG_LEVEL', 'INFO')

        self._setup_logging()

    def _setup_logging(self) -> None:
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('lead_finder.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def validate(self) -> None:
        """Validate required configuration on startup"""
        errors = []

        if not self.BRIGHT_DATA_API_KEY:
            errors.append("BRIGHT_DATA_API_KEY is required")

        if not self.AIML_API_KEY:
            errors.append("AIML_API_KEY is required")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    # ── Getters ──────────────────────────────────────────────────────────────

    def get_bright_data_api_key(self) -> str:
        return self.BRIGHT_DATA_API_KEY

    def get_serp_zone(self) -> str:
        return self.BRIGHT_DATA_SERP_ZONE

    def get_unlocker_zone(self) -> str:
        return self.BRIGHT_DATA_UNLOCKER_ZONE

    def get_bright_data_endpoint(self) -> str:
        return self.BRIGHT_DATA_ENDPOINT

    def get_aiml_api_key(self) -> str:
        return self.AIML_API_KEY

    def get_aiml_model(self) -> str:
        return self.AIML_MODEL

    def get_aiml_base_url(self) -> str:
        return self.AIML_BASE_URL

    def get_timeout(self) -> int:
        return self.REQUEST_TIMEOUT

    def get_max_concurrent(self) -> int:
        return self.MAX_CONCURRENT_REQUESTS

    def get_max_retries(self) -> int:
        return self.MAX_RETRIES


# Global singleton
config = Config()
