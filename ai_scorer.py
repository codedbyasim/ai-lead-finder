"""
AI Scorer Module
Analyzes leads using AIML API (claude-opus-4-8 or any AIML-supported model).
AIML API is OpenAI-compatible, so we use the openai SDK pointed at AIML's base URL.
"""

import json
import logging
from typing import Dict
from dataclasses import dataclass
from config import config

logger = logging.getLogger(__name__)


@dataclass
class LeadScore:
    """Result of AI lead analysis"""
    score: int            # 0-100
    category: str         # High / Medium / Low
    problem_detected: str
    suggested_service: str
    pitch_urdu: str
    pitch_english: str
    analysis_details: Dict


class AIScorer:
    """Scores leads using AIML API (OpenAI-compatible)"""

    def __init__(self):
        self.api_key  = config.get_aiml_api_key()
        self.model    = config.get_aiml_model()
        self.base_url = config.get_aiml_base_url()
        self.client   = self._init_client()
        self._quota_exceeded = False  # flip to True on 403 quota error

    # ── Init ─────────────────────────────────────────────────────────────────

    def _init_client(self):
        """
        AIML API is OpenAI-compatible.
        We just point the openai SDK to AIML's base URL.
        """
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            logger.info(f"AIML API initialized — model: {self.model}")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize AIML client: {e}")
            return None

    # ── Main scoring ─────────────────────────────────────────────────────────

    def score_lead(self, contact_info, niche: str, service: str) -> LeadScore:
        """Score a lead using AI, with rule-based fallback if quota exceeded"""
        logger.info(f"Scoring: {contact_info.business_name}")

        if not self.client or self._quota_exceeded:
            return self._rule_based_score(contact_info, service)

        prompt = self._build_prompt(contact_info, niche, service)

        try:
            raw = self._call_aiml(prompt)
            result = self._parse_response(raw)

            score_val = int(result.get("score", 50))
            score_val = max(0, min(100, score_val))

            lead_score = LeadScore(
                score=score_val,
                category=self._categorize(score_val),
                problem_detected=result.get("problem", "No specific problem detected"),
                suggested_service=result.get("suggestion", service),
                pitch_urdu=result.get("pitch_urdu", ""),
                pitch_english=result.get("pitch_english", ""),
                analysis_details=result,
            )
            logger.info(f"Scored {contact_info.business_name}: {score_val}/100 ({lead_score.category})")
            return lead_score

        except Exception as e:
            err_str = str(e)
            # Quota exceeded — stop calling API for remaining leads
            if "quota exceeded" in err_str.lower() or "ALL_TIME_LIMIT" in err_str:
                logger.warning("AIML quota exceeded — switching to rule-based scoring")
                self._quota_exceeded = True
                return self._rule_based_score(contact_info, service)

            logger.error(f"Scoring error for {contact_info.business_name}: {e}")
            return self._rule_based_score(contact_info, service)

    # ── AIML API call ─────────────────────────────────────────────────────────

    def _call_aiml(self, prompt: str) -> str:
        """Send prompt to AIML API and return raw text response"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert freelance AI consultant. "
                        "Analyze the given business and return ONLY valid JSON — "
                        "no markdown, no extra text."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=15000,  # Gemini 2.5 Flash needs higher limit (reasoning model)
        )
        content = response.choices[0].message.content

        # Gemini reasoning models sometimes return empty content if tokens too low
        if not content or not content.strip():
            finish = response.choices[0].finish_reason
            raise ValueError(f"Empty response from model (finish_reason={finish})")

        return content

    # ── Prompt builder ────────────────────────────────────────────────────────

    def _build_prompt(self, contact_info, niche: str, service: str) -> str:
        has_email    = len(contact_info.emails) > 0
        has_phone    = len(contact_info.phones) > 0
        has_whatsapp = contact_info.whatsapp is not None
        techs        = ", ".join(contact_info.technologies) or "Unknown"
        services     = ", ".join(contact_info.services[:5]) or "None detected"
        description  = (contact_info.meta_description or "N/A")[:200]

        return f"""Analyze this Pakistani business as a potential client for freelance AI/dev services.

Business Details:
- Name        : {contact_info.business_name}
- Website     : {contact_info.url}
- Niche       : {niche}
- Has Chatbot : {contact_info.has_chatbot}
- Has Email   : {has_email}
- Has Phone   : {has_phone}
- Has WhatsApp: {has_whatsapp}
- Technologies: {techs}
- Services    : {services}
- Description : {description}

Service I want to offer: {service}

Scoring guide:
- No chatbot          → +20 pts
- No online booking   → +15 pts
- Poor contact info   → +10 pts
- Outdated tech stack → +15 pts
- Strong niche match  → +20 pts
- Active website      → +10 pts
- Multiple services   → +10 pts

Return ONLY this JSON (no markdown):
{{
  "score": 85,
  "problem": "No chatbot; customers cannot get instant help",
  "suggestion": "AI WhatsApp Chatbot for customer support",
  "pitch_urdu": "Assalamualaikum! Maine aapki website dekhi aur notice kiya ke aapke paas customer queries ke liye chatbot nahi hai. Hum aapke liye AI-powered WhatsApp bot bana sakte hain jo 24/7 customers ki madad kare.",
  "pitch_english": "Hello! I visited your website and noticed there is no chatbot for customer queries. We can build an AI-powered WhatsApp bot that handles customer support 24/7."
}}"""

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _parse_response(self, raw: str) -> Dict:
        """Strip markdown fences and parse JSON"""
        text = raw.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw: {raw[:300]}")
            return {
                "score": 50,
                "problem": "Analysis incomplete",
                "suggestion": service if hasattr(self, '_last_service') else "AI Services",
                "pitch_urdu": "Assalamualaikum! Hum aapke business ke liye AI solutions provide karte hain.",
                "pitch_english": "Hello! We provide AI solutions for your business.",
            }

    def _categorize(self, score: int) -> str:
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Medium"
        return "Low"

    def _default_score(self, contact_info, service: str) -> LeadScore:
        return LeadScore(
            score=0,
            category="Low",
            problem_detected="Analysis failed — AIML API unavailable",
            suggested_service=service,
            pitch_urdu="Assalamualaikum! Hum aapke business ke liye AI solutions provide karte hain.",
            pitch_english="Hello! We provide AI solutions for your business.",
            analysis_details={},
        )

    def _rule_based_score(self, contact_info, service: str) -> LeadScore:
        """
        Score a lead using simple rules — no AI needed.
        Used when AIML quota is exceeded or API is unavailable.
        """
        score = 40  # base score

        # No chatbot → high potential
        if not contact_info.has_chatbot:
            score += 20

        # Has contact info → reachable
        if contact_info.emails:
            score += 10
        if contact_info.phones:
            score += 5
        if contact_info.whatsapp:
            score += 5

        # Outdated tech → needs upgrade
        if "WordPress" in contact_info.technologies:
            score += 10
        if not contact_info.technologies:
            score += 5  # unknown tech = likely outdated

        # Has services listed → active business
        if contact_info.services:
            score += 5

        score = min(score, 95)  # cap at 95 (100 reserved for AI-confirmed)

        # Detect problem
        problems = []
        if not contact_info.has_chatbot:
            problems.append("No chatbot for customer queries")
        if not contact_info.emails:
            problems.append("No email address found")
        if not contact_info.whatsapp:
            problems.append("No WhatsApp contact")
        problem = "; ".join(problems) if problems else "Could benefit from AI automation"

        # Build pitch
        biz = contact_info.business_name
        pitch_urdu = (
            f"Assalamualaikum! Maine {biz} ki website dekhi. "
            f"{problem}. Hum aapke liye {service} provide kar sakte hain. "
            f"Kya aap baat karna chahen ge?"
        )
        pitch_english = (
            f"Hello! I visited {biz}'s website and noticed: {problem}. "
            f"We can provide {service} to help. Would you like to discuss?"
        )

        return LeadScore(
            score=score,
            category=self._categorize(score),
            problem_detected=problem,
            suggested_service=service,
            pitch_urdu=pitch_urdu,
            pitch_english=pitch_english,
            analysis_details={"method": "rule_based"},
        )

    def generate_pitch(self, business_name: str, problem: str, service: str, language: str = "urdu") -> str:
        """Generate a standalone pitch message"""
        if language.lower() == "urdu":
            return (
                f"Assalamualaikum! Maine {business_name} ki website dekhi. "
                f"{problem}. Hum aapke liye {service} provide kar sakte hain. "
                f"Kya aap is baare mein baat karna chahen ge?"
            )
        return (
            f"Hello! I visited {business_name}'s website and noticed: {problem}. "
            f"We can provide {service} to solve this. Would you like to discuss?"
        )
