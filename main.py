#!/usr/bin/env python3
"""AI Email Agent - Main entry point

Local AI email processing agent using Ollama.
Analyzes emails, classifies intent, generates draft responses.

Author: kokgfnu
Contact: kokgfnu@gmail.com
License: MIT
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.config import get_config
from src.email_parser import EmailParser
from src.ai_analyzer import AIAnalyzer
from src.storage import EmailStorage
from src.response_generator import ResponseGenerator


async def process_email(email_data):
    """Process a single email through the full pipeline"""
    print(f"Processing email: {email_data.subject}")
    print(f"From: {email_data.from_email}")

    # Check if already processed (idempotent)
    storage = EmailStorage()
    if await storage.is_processed(email_data):
        print("Email already processed (idempotent check)")
        return None

    # Analyze with AI
    print("Analyzing with Ollama...")
    analyzer = AIAnalyzer()
    analysis = await analyzer.analyze(email_data)

    print(f"Priority: {analysis.priority}")
    print(f"Intent: {analysis.intent}")
    print(f"Action: {analysis.required_action}")
    print(f"Summary: {analysis.summary}")
    print(f"Key points: {analysis.key_points}")
    print(f"Confidence: {analysis.confidence:.2f}")

    # Generate draft reply
    generator = ResponseGenerator()
    draft = generator.format_reply(email_data, analysis)

    # Save to database
    await storage.init_db()
    await storage.save_email(email_data, analysis, datetime.now().isoformat())

    # Output results
    result = {
        "email_id": storage.generate_email_id(email_data),
        "analysis": {
            "priority": analysis.priority,
            "intent": analysis.intent,
            "required_action": analysis.required_action,
            "summary": analysis.summary,
            "key_points": analysis.key_points,
            "confidence": analysis.confidence
        },
        "draft_reply": draft,
        "processed_at": datetime.now().isoformat()
    }

    print("\n--- Analysis Result ---")
    print(json.dumps(result, indent=2))

    return result


async def start_server():
    """Start the webhook server"""
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    config = get_config()
    app = FastAPI(title="AI Email Agent")

    storage = EmailStorage(config.DB_PATH)

    @app.on_event("startup")
    async def startup():
        await storage.init_db()

    @app.post("/webhook")
    async def webhook(email: dict):
        """Process email sent via webhook"""
        email_data = EmailParser.from_json(email)
        result = await process_email(email_data)
        if result:
            return JSONResponse(content={"status": "processed", "result": result})
        return JSONResponse(content={"status": "already_processed"})

    @app.get("/recent")
    async def recent():
        """Get recently processed emails"""
        emails = await storage.get_recent_emails(10)
        return {"emails": emails}

    @app.get("/health")
    async def health():
        """Health check - verify Ollama connection"""
        config = get_config()
        ollama_ok = config.check_ollama()
        return {
            "status": "ok",
            "ollama": "connected" if ollama_ok else "disconnected",
            "model": config.OLLAMA_MODEL
        }

    print(f"Starting server on port {config.PORT}")
    print("Endpoints:")
    print("  POST /webhook - Process email")
    print("  GET  /recent  - Recent emails")
    print("  GET  /health  - Health check")
    print("Press Ctrl+C to stop")

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Email Agent")
    parser.add_argument("--email", "-e", help="Path to email JSON file")
    parser.add_argument("--stdin", "-s", action="store_true", help="Read email from stdin")
    parser.add_argument("--server", "-p", action="store_true", help="Start webhook server")

    args = parser.parse_args()

    if args.server:
        await start_server()
        return

    # Get email data
    if args.email:
        email_data = EmailParser.from_file(args.email)
    elif args.stdin:
        email_data = EmailParser.from_stdin()
    else:
        # Use demo email if no input provided
        print("No input provided. Using demo email.")
        demo = {
            "from": "client@example.com",
            "to": "me@example.com",
            "subject": "Meeting request for next week",
            "body": "Hi, I'd like to schedule a meeting next Tuesday at 3pm to discuss the project timeline. Please let me know if that works for you. Also, we need to finalize the budget before the end of the month.\n\nBest regards",
            "date": datetime.now().isoformat()
        }
        email_data = EmailParser.from_json(demo)

    # Process the email
    result = await process_email(email_data)

    if result:
        print("\nDraft reply:")
        print(result["draft_reply"])


if __name__ == "__main__":
    asyncio.run(main())
