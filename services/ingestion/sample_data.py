"""Sample ingestion data for local Phase 1 testing.

This module provides deterministic fixture-like records until live Graph
connectors are wired in a later phase.
"""

from __future__ import annotations


def load_sample_email_events() -> list[dict[str, object]]:
    return [
        {
            "message_id": "msg-1001",
            "subject": "CW 165739 - customer follow-up needed",
            "source": "sample",
            "classification": "ticket_update",
            "confidence": 0.98,
            "payload": {
                "ticketId": "165739",
                "system": "ConnectWise",
                "from": "customer@example.com",
                "snippet": "Please confirm the next maintenance window.",
            },
        },
        {
            "message_id": "msg-1002",
            "subject": "Meeting prep for Thursday steering committee",
            "source": "sample",
            "classification": "meeting_prep",
            "confidence": 0.92,
            "payload": {
                "meetingId": "mtg-2001",
                "agenda": ["status", "risks", "decisions"],
            },
        },
    ]
