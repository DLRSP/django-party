"""Consent ledger helpers — null/unknown is not granted."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.db import transaction
from django.utils import timezone as dj_timezone

from party.models import ConsentRecord, Party

# Beddy / PMS flags that must never become ConsentRecord rows.
BEDDY_CONSENT_FORBIDDEN_KEYS = frozenset(
    {
        "privacy_check",
        "privacy_check_from_admin",
        "promotion_check",
        "promotion_check_from_admin",
        "privacy_date",
        "promotion_date",
    }
)


def latest_consent(party: Party, purpose: str) -> Optional[ConsentRecord]:
    return (
        ConsentRecord.objects.filter(party=party, purpose=purpose)
        .order_by("-recorded_at")
        .first()
    )


def marketing_allowed(party: Party) -> bool:
    """Only explicit granted (not withdrawn later) allows marketing send."""
    row = latest_consent(party, ConsentRecord.Purpose.MARKETING)
    return bool(row and row.decision == ConsentRecord.Decision.GRANTED)


@transaction.atomic
def record_consent(
    party: Party,
    *,
    purpose: str,
    decision: str,
    source: str = "",
    recorded_at: Optional[datetime] = None,
) -> ConsentRecord:
    """Sole supported write path for ConsentRecord (append-only)."""
    if purpose not in ConsentRecord.Purpose.values:
        raise ValueError(f"Invalid consent purpose: {purpose}")
    if decision not in ConsentRecord.Decision.values:
        raise ValueError(f"Invalid consent decision: {decision}")
    src = (source or "").strip()
    if any(k in src for k in BEDDY_CONSENT_FORBIDDEN_KEYS):
        raise ValueError(
            "Consent source must not encode PMS privacy/promotion flags; "
            "use an explicit HITL or portal capture path."
        )
    return ConsentRecord.objects.create(
        party=party,
        purpose=purpose,
        decision=decision,
        source=src,
        recorded_at=recorded_at or dj_timezone.now(),
    )


def refuse_beddy_consent_mapping(payload: dict) -> None:
    """Raise if a caller tries to map Beddy privacy/promo bits into consent."""
    if not isinstance(payload, dict):
        return
    hit = BEDDY_CONSENT_FORBIDDEN_KEYS.intersection(payload.keys())
    if hit:
        raise ValueError(
            f"Refusing Beddy→ConsentRecord mapping for keys: {sorted(hit)}"
        )
