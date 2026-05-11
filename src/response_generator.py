# Response generator module
# Creates formatted draft email responses based on AI analysis

from .email_parser import EmailData
from .ai_analyzer import EmailAnalysis


class ResponseGenerator:
    """Generate draft email responses"""

    def format_reply(self, email: EmailData, analysis: EmailAnalysis) -> str:
        """Create a formatted draft reply"""
        if analysis.suggested_reply:
            # Use AI-generated reply if available
            return self._enhance_format(analysis.suggested_reply, email)

        # Generate template reply based on intent
        template = self._get_template(analysis.intent, analysis.required_action)
        return template.format(
            sender=email.from_email,
            subject=email.subject
        )

    def _enhance_format(self, reply: str, email: EmailData) -> str:
        """Add formatting and context to the reply"""
        formatted = f"Draft Reply:\n{'='*40}\n"
        formatted += f"To: {email.from_email}\n"
        formatted += f"Subject: Re: {email.subject}\n\n"
        formatted += reply
        return formatted

    def _get_template(self, intent: str, action: str) -> str:
        """Get response template based on email intent"""
        templates = {
            ("request", "reply"): """Hi,

Thank you for your email regarding {subject}.

I've received your request and will review it shortly.
I'll get back to you with a detailed response within 24 hours.

Best regards""",

            ("information", "file"): """Hi,

Thank you for sharing this information.

I've saved this for future reference.
If I have any questions, I'll reach out.

Best regards""",

            ("notification", "ignore"): """Hi,

Acknowledged. Thank you for the update.

Best regards""",

            ("urgent", "reply"): """Hi,

I've received your urgent message regarding {subject}.

I'm prioritizing this and will respond within the next few hours.

Best regards""",

            ("spam", "ignore"): "",
        }

        key = (intent, action)
        return templates.get(key, templates[("information", "file")])
