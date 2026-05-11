# Email parser module
# Parses raw email data into structured format for AI analysis

import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class EmailData:
    """Structured email data extracted from raw input"""
    from_email: str
    to_email: str
    subject: str
    body: str
    date: Optional[str] = None
    html_body: Optional[str] = None

    def to_plain_text(self) -> str:
        """Convert HTML body to plain text if available"""
        if self.html_body:
            # Simple HTML stripping - remove tags
            text = self.html_body
            while "<" in text and ">" in text:
                start = text.index("<")
                end = text.index(">")
                text = text[:start] + text[end + 1:]
            return text
        return self.body

    def summary(self) -> str:
        """Create a short summary for AI processing"""
        return f"From: {self.from_email}\nSubject: {self.subject}\n\n{self.body[:2000]}"


class EmailParser:
    """Parse email data from various formats"""

    @staticmethod
    def from_json(data: dict) -> EmailData:
        """Parse email from JSON dictionary"""
        return EmailData(
            from_email=data.get("from", "unknown"),
            to_email=data.get("to", "unknown"),
            subject=data.get("subject", "No subject"),
            body=data.get("body", ""),
            date=data.get("date"),
            html_body=data.get("html_body")
        )

    @staticmethod
    def from_file(filepath: str) -> EmailData:
        """Parse email from JSON file"""
        with open(filepath, "r") as f:
            data = json.load(f)
        return EmailParser.from_json(data)

    @staticmethod
    def from_stdin() -> EmailData:
        """Parse email from stdin"""
        import sys
        data = json.loads(sys.stdin.read())
        return EmailParser.from_json(data)
