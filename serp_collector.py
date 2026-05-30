"""
SERP Collector Module
Searches Google for business websites using Bright Data SERP API.

Correct method: Direct REST API (POST to api.brightdata.com/request)
Docs: https://docs.brightdata.com/api-reference/rest-api/serp/serp-api
"""

import requests
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from config import config
from utils import validate_url

logger = logging.getLogger(__name__)


@dataclass
class BusinessURL:
    """A single business found via SERP"""
    url: str
    business_name: str
    description: str
    phone: Optional[str] = None
    source: str = 'serp'


class SERPCollector:
    """Collects business URLs from Google via Bright Data SERP REST API"""

    BRIGHT_DATA_ENDPOINT = "https://api.brightdata.com/request"

    def __init__(self):
        self.api_key     = config.get_bright_data_api_key()
        self.zone        = config.get_serp_zone()          # e.g. serp_api2
        self.timeout     = config.get_timeout()
        self.max_retries = config.get_max_retries()

    # ── Query generation ─────────────────────────────────────────────────────

    def generate_queries(self, niche: str, city: str, service: str = "") -> List[str]:
        """Return a list of Google search query strings"""
        queries = [
            f"{niche} in {city} contact website",
            f"{niche} agencies {city} phone email",
            f"{niche} {city} services contact information",
            f"best {niche} {city} website",
        ]
        if service:
            queries.insert(1, f"{niche} {city} {service} contact")

        logger.info(f"Generated {len(queries)} queries for '{niche}' in '{city}'")
        return queries

    # ── Single search ────────────────────────────────────────────────────────

    def search(self, query: str) -> Dict:
        """
        POST to Bright Data SERP REST API.
        Uses format=raw and parses HTML since some zones don't support JSON format.
        """
        google_url = (
            f"https://www.google.com/search"
            f"?q={requests.utils.quote(query)}"
            f"&num=10&gl=pk&hl=en"
        )

        payload = {
            "zone":   self.zone,
            "url":    google_url,
            "format": "raw",   # raw HTML — more compatible across zone types
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }

        logger.info(f"SERP search: {query}")

        response = requests.post(
            self.BRIGHT_DATA_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        # Return raw HTML string wrapped in a dict
        return {"raw_html": response.text, "query": query}

    # ── Parse results ────────────────────────────────────────────────────────

    def parse_results(self, data: Dict) -> List[BusinessURL]:
        """
        Parse raw Google HTML returned by Bright Data.
        Extracts organic result links, titles, and snippets.
        """
        from bs4 import BeautifulSoup
        import re

        businesses = []
        html = data.get("raw_html", "")

        if not html:
            logger.warning("Empty HTML in SERP response")
            return businesses

        soup = BeautifulSoup(html, "lxml")

        # Strategy 1: <div class="g"> blocks (standard Google layout)
        for result in soup.select("div.g"):
            try:
                a_tag = result.select_one("a[href]")
                if not a_tag:
                    continue
                url = a_tag.get("href", "")
                if not url.startswith("http"):
                    continue
                # Skip Google internal URLs
                if "google.com" in url:
                    continue
                if not validate_url(url):
                    continue

                title_tag = result.select_one("h3")
                title = title_tag.get_text(strip=True) if title_tag else ""

                # Try multiple snippet selectors
                snippet = ""
                for sel in ["div.VwiC3b", "span.aCOpRe", "div[data-sncf]",
                            "div.IsZvec", "div.s", "span.st"]:
                    el = result.select_one(sel)
                    if el:
                        snippet = el.get_text(strip=True)
                        break

                if not title:
                    title = url

                phone = self._extract_phone_from_text(snippet)
                businesses.append(BusinessURL(
                    url=url,
                    business_name=title,
                    description=snippet,
                    phone=phone,
                ))
            except Exception as e:
                logger.debug(f"Skipping result: {e}")
                continue

        # Strategy 2: Fallback — grab all external links from the page
        if not businesses:
            logger.info("Strategy 1 found nothing, trying fallback link extraction")
            seen = set()
            for a in soup.find_all("a", href=True):
                url = a["href"]
                if not url.startswith("http"):
                    continue
                # Skip junk domains — not real business leads
                if _is_junk_url(url):
                    continue
                if not validate_url(url):
                    continue
                if url in seen:
                    continue
                seen.add(url)

                title = a.get_text(strip=True) or url
                # Skip very short or generic titles
                if len(title) < 5 or title.lower() in ("website", "home", "click here"):
                    title = url

                businesses.append(BusinessURL(
                    url=url,
                    business_name=title[:120],
                    description="",
                    phone=None,
                ))

                if len(businesses) >= 10:
                    break

        logger.info(f"Parsed {len(businesses)} businesses from SERP HTML")
        return businesses

    def _extract_phone_from_text(self, text: str) -> Optional[str]:
        import re
        patterns = [
            r'\+92[-\s]?\d{2,4}[-\s]?\d{7,8}',
            r'0\d{2,4}[-\s]?\d{7,8}',
        ]
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                return m.group(0)
        return None

    def _retry_request(self, query: str) -> Dict:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return self.search(query)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed ({e}), retrying in {wait}s…")
                    time.sleep(wait)
        raise last_error

    # ── Main collection ──────────────────────────────────────────────────────

    def collect_urls(self, queries: List[str], count: int) -> List[BusinessURL]:
        """Collect up to `count` unique business URLs across all queries"""
        all_businesses: List[BusinessURL] = []
        seen_base_urls: set = set()   # deduplicate by base URL (ignore fragments)

        for query in queries:
            if len(all_businesses) >= count:
                break
            try:
                data       = self._retry_request(query)
                businesses = self.parse_results(data)

                for biz in businesses:
                    # Strip fragment (#:~:text=...) for deduplication
                    base = biz.url.split('#')[0].rstrip('/')
                    if base in seen_base_urls:
                        continue
                    seen_base_urls.add(base)
                    # Store clean URL without fragment
                    biz.url = base
                    all_businesses.append(biz)
                    if len(all_businesses) >= count:
                        break

                time.sleep(1)   # polite delay

            except Exception as e:
                logger.error(f"Failed query '{query}': {e}")
                continue

        logger.info(f"Collected {len(all_businesses)} unique URLs")
        return all_businesses[:count]


# ── Module-level helpers ──────────────────────────────────────────────────────

# Domains that are NOT real business leads — filter these out
_JUNK_DOMAINS = {
    # Search engines & their products
    "google.com", "google.co.in", "google.ca", "google.co.uk",
    "google.com.pk", "gstatic.com", "googleapis.com",
    "bing.com", "yahoo.com", "duckduckgo.com",
    # Social media (not direct business websites)
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "youtube.com", "tiktok.com",
    # Document / aggregator sites
    "scribd.com", "slideshare.net", "academia.edu",
    "wikipedia.org", "wikimedia.org",
    # News / blogs
    "dawn.com", "geo.tv", "tribune.com.pk", "bbc.com", "cnn.com",
    # Maps / directories (not the business itself)
    "maps.google.com",
}


def _is_junk_url(url: str) -> bool:
    """Return True if the URL belongs to a domain we should skip."""
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lower()
        # Strip www.
        if host.startswith("www."):
            host = host[4:]
        # Check exact match or subdomain match
        for junk in _JUNK_DOMAINS:
            if host == junk or host.endswith("." + junk):
                return True
        return False
    except Exception:
        return False
