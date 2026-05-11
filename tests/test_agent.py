#!/usr/bin/env python3
"""Tests for AI Email Agent"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.email_parser import EmailParser
from src.storage import EmailStorage


def test_email_parser_from_json():
    """Test parsing email from JSON"""
    data = {
        "from": "test@example.com",
        "to": "recipient@example.com",
        "subject": "Test subject",
        "body": "Test body content"
    }
    email = EmailParser.from_json(data)
    assert email.from_email == "test@example.com"
    assert email.subject == "Test subject"
    assert email.body == "Test body content"
    print("PASS: from_json")


def test_email_parser_from_file():
    """Test parsing email from file"""
    email = EmailParser.from_file(os.path.join(os.path.dirname(__file__), "..", "demo_email.json"))
    assert email.from_email == "client@example.com"
    assert email.subject == "Meeting request for next week"
    print("PASS: from_file")


def test_email_summary():
    """Test email summary generation"""
    data = {
        "from": "test@example.com",
        "to": "recipient@example.com",
        "subject": "Test",
        "body": "Hello world"
    }
    email = EmailParser.from_json(data)
    summary = email.summary()
    assert "test@example.com" in summary
    assert "Test" in summary
    print("PASS: summary")


def test_storage_id_generation():
    """Test email ID generation"""
    storage = EmailStorage(":memory:")
    data = {
        "from": "test@example.com",
        "to": "recipient@example.com",
        "subject": "Test",
        "body": "Hello"
    }
    email = EmailParser.from_json(data)
    email_id = storage.generate_email_id(email)
    assert len(email_id) == 16
    # Same input should give same ID
    email_id2 = storage.generate_email_id(email)
    assert email_id == email_id2
    print("PASS: id generation")


if __name__ == "__main__":
    test_email_parser_from_json()
    test_email_parser_from_file()
    test_email_summary()
    test_storage_id_generation()
    print("\nAll tests passed!")
