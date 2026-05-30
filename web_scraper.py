"""
Web Scraper Module
Fetches website HTML via Bright Data Web Unlocker REST API (Direct API access).

Correct method: POST https://api.brightdata.com/request
  {"zone": "web_unlocker1", "url": "<target>", "format": "raw"}
Docs: https://docs.brightdata.com/scraping-automation/web-unlocker/send-your-first-request
"""

import requests
import logging
from typing import List, Optional
from dataclasses import dataclass, field
from config import config
from utils import extract_emails_from_text, extract_phones_from_text, normalize_text

logger = logging.getLogger(__name__)

BRIGHT_DATA_ENDPOINT = "https://api.brightdata.com/request"


@dataclass
class ContactInfo:
    """All extracted data for one website"""
    url: str
    business_name: str
    emails: List[str]        = field(default_factory=list)
    phones: List[str]        = field(default_factory=list)
    whatsapp: Optional[str]  = None
    has_chatbot: bool        = False
    technologies: List[str]  = field(default_factory=list)
    services: List[str]      = field(default_factory=list)
    page_title: str          = ""
    meta_description: str    = ""


class WebScraper:
    """Fetches and parses websites via Bright Data Web Unlocker REST API"""

    def __init__(self):
        self.api_key     = config.get_bright_data_api_key()
        self.zone        = config.get_unlocker_zone()      # e.g. web_unlocker1
        self.timeout     = config.get_timeout()
        self.max_retries = config.get_max_retries()

    # ── Fetch ────────────────────────────────────────────────────────────────

    def fetch_url(self, url: str) -> str:
        """
        Fetch website HTML through Bright Data Web Unlocker REST API.
        Returns raw HTML string.
        """
        logger.info(f"Fetching: {url}")

        payload = {
            "zone":   self.zone,
            "url":    url,
            "format": "raw",
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    BRIGHT_DATA_ENDPOINT,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                return response.text

            except requests.exceptions.Timeout:
                last_error = Exception(f"Timeout fetching {url}")
                logger.warning(f"Timeout on {url} (attempt {attempt + 1})")
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"Error fetching {url} (attempt {attempt + 1}): {e}")

            if attempt < self.max_retries - 1:
                import time
                time.sleep(2 ** attempt)

        raise last_error

    # ── Main extraction ──────────────────────────────────────────────────────

    def extract_contact_info(self, html: str, url: str) -> ContactInfo:
        """Parse HTML and extract all useful contact/business data"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator=" ", strip=True)

        return ContactInfo(
            url=url,
            business_name=self._extract_business_name(soup, url),
            emails=self.extract_emails(text),
            phones=self.extract_phones(text),
            whatsapp=self.extract_whatsapp(html, text),
            has_chatbot=self.detect_chatbot(html),
            technologies=self.detect_technologies(html),
            services=self.extract_services(soup),
            page_title=self._extract_title(soup),
            meta_description=self._extract_meta_description(soup),
        )

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _extract_business_name(self, soup, url: str) -> str:
        from utils import extract_domain
        for tag in ["title", "h1"]:
            el = soup.find(tag)
            if el:
                return normalize_text(el.get_text())
        return extract_domain(url)

    def _extract_title(self, soup) -> str:
        el = soup.find("title")
        return normalize_text(el.get_text()) if el else ""

    def _extract_meta_description(self, soup) -> str:
        el = soup.find("meta", attrs={"name": "description"})
        return normalize_text(el["content"]) if el and el.get("content") else ""

    def extract_emails(self, text: str) -> List[str]:
        return extract_emails_from_text(text)

    def extract_phones(self, text: str) -> List[str]:
        return extract_phones_from_text(text)

    def extract_whatsapp(self, html: str, text: str) -> Optional[str]:
        import re
        m = re.search(r'wa\.me/(\d+)', html)
        if m:
            return f"+{m.group(1)}"
        if "whatsapp" in text.lower():
            m2 = re.search(r'whatsapp.{0,50}(\+?\d[\d\s\-]{8,})', text, re.IGNORECASE)
            if m2:
                return m2.group(1).strip()
        return None

    def detect_chatbot(self, html: str) -> bool:
        indicators = [
            "tawk.to", "intercom.com", "drift.com", "crisp.chat",
            "livechat", "zendesk", "tidio", "freshchat",
            "chatbot", "messenger-plugin",
        ]
        html_lower = html.lower()
        return any(ind in html_lower for ind in indicators)

    def detect_technologies(self, html: str) -> List[str]:
        tech_map = {
            "WordPress": ["wp-content", "wp-includes"],
            "Shopify":   ["shopify", "cdn.shopify.com"],
            "Wix":       ["wix.com", "wixstatic.com"],
            "React":     ["react", "reactjs"],
            "Vue":       ["vue.js", "vuejs"],
            "Angular":   ["angular", "ng-"],
            "jQuery":    ["jquery"],
            "Bootstrap": ["bootstrap"],
        }
        html_lower = html.lower()
        return [
            tech for tech, patterns in tech_map.items()
            if any(p in html_lower for p in patterns)
        ]

    def extract_services(self, soup) -> List[str]:
        keywords = [
            "service", "solution", "offering", "product",
            "chatbot", "automation", "dashboard", "scraping",
            "booking", "appointment", "consultation",
        ]
        services = []
        for tag in soup.find_all(["h2", "h3", "h4", "li"]):
            text = tag.get_text().lower()
            if any(kw in text for kw in keywords):
                services.append(normalize_text(tag.get_text()))
        return list(set(services))[:10]
