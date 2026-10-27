"""Consent ledger helpers — null/unknown is not granted."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone as dj_timezone

from party.models import ConsentRecord, Party


def untrusted_consent_payload_keys() -> frozenset[str]:
    """Consumer-configured PMS/IdP payload keys that must never become consent.

    Default empty — adopters set ``PARTY_CONSENT_FORBIDDEN_PAYLOAD_KEYS`` in settings.
    """
    configured = getattr(settings, "PARTY_CONSENT_FORBIDDEN_PAYLOAD_KEYS", None)
    if not configured:
        return frozenset()
    return frozenset(configured)


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
    forbidden = untrusted_consent_payload_keys()
    if forbidden and any(k in src for k in forbidden):
        raise ValueError(
            "Consent source must not encode PMS privacy/promotion flags; "
            "use an explicit operator or portal capture path."
        )
    return ConsentRecord.objects.create(
        party=party,
        purpose=purpose,
        decision=decision,
        source=src,
        recorded_at=recorded_at or dj_timezone.now(),
    )


def refuse_untrusted_consent_mapping(
    payload: dict,
    *,
    forbidden_keys: Optional[Iterable[str]] = None,
) -> None:
    """Raise if payload keys must not be mapped into ConsentRecord."""
    if not isinstance(payload, dict):
        return
    keys = (
        frozenset(forbidden_keys)
        if forbidden_keys is not None
        else untrusted_consent_payload_keys()
    )
    if not keys:
        return
    hit = keys.intersection(payload.keys())
    if hit:
        raise ValueError(
            f"Refusing untrusted→ConsentRecord mapping for keys: {sorted(hit)}"
        )
