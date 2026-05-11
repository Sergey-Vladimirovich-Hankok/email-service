# AI analyzer module
# Sends email data to local Ollama model for analysis

import json
import httpx
from dataclasses import dataclass
from typing import Optional

from .config import get_config
from .email_parser import EmailData


@dataclass
class EmailAnalysis:
    """Result of AI email analysis"""
    priority: str  # "high", "medium", "low"
    intent: str  # "request", "information", "notification", "spam"
    required_action: str  # "reply", "schedule", "file", "ignore"
    summary: str  # One-line summary of the email
    key_points: list  # Important points extracted
    suggested_reply: Optional[str] = None
    entities: dict = None  # Dates, names, locations found
    confidence: float = 0.0  # How confident the AI is


class AIAnalyzer:
    """Analyze emails using local Ollama model"""

    def __init__(self):
        self.config = get_config()
        self.model = self.config.OLLAMA_MODEL
        self.host = self.config.OLLAMA_HOST
        self.prompt = self.config.SYSTEM_PROMPT

    def build_prompt(self, email: EmailData) -> str:
        """Build the analysis prompt for the AI model"""
        return f"""{self.prompt}

Analyze this email and return JSON:

Email:
{email.summary()}

Return ONLY valid JSON with these fields:
{{
  "priority": "high|medium|low",
  "intent": "request|information|notification|spam|urgent",
  "required_action": "reply|schedule|file|ignore|escalate",
  "summary": "one line summary",
  "key_points": ["point1", "point2"],
  "suggested_reply": "draft reply text or null if not needed",
  "entities": {{"dates": [], "names": [], "locations": []}},
  "confidence": 0.0 to 1.0
}}

Rules:
- priority "high" for deadlines, urgent requests, money matters
- intent: what the sender wants
- required_action: what the recipient should do
- Be concise and accurate"""

    async def analyze(self, email: EmailData) -> EmailAnalysis:
        """Send email to Ollama and get analysis result"""
        prompt = self.build_prompt(email)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 1024
                    }
                }
            )

            response.raise_for_status()
            result = response.json()

        # Extract and parse the AI response
        text = result.get("response", "")
        analysis = self._parse_response(text)

        return analysis

    def _parse_response(self, text: str) -> EmailAnalysis:
        """Parse JSON response from Ollama"""
        # Try to find JSON in the response
        try:
            # Find JSON block between curly braces
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                data = json.loads(json_str)
            else:
                # Fallback: try parsing entire text
                data = json.loads(text)
        except json.JSONDecodeError:
            # If parsing fails, return default analysis
            data = {
                "priority": "medium",
                "intent": "information",
                "required_action": "file",
                "summary": "Could not analyze email",
                "key_points": [],
                "suggested_reply": None,
                "entities": {"dates": [], "names": [], "locations": []},
                "confidence": 0.0
            }

        # Ensure all fields are present
        return EmailAnalysis(
            priority=data.get("priority", "medium"),
            intent=data.get("intent", "information"),
            required_action=data.get("required_action", "file"),
            summary=data.get("summary", ""),
            key_points=data.get("key_points", []),
            suggested_reply=data.get("suggested_reply"),
            entities=data.get("entities", {}),
            confidence=data.get("confidence", 0.0)
        )
