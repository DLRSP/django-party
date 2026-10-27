"""PartyFact upsert helpers — refuse fiscal/token keys."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.db import transaction
from django.utils import timezone as dj_timezone

from party.models import Party, PartyFact
from party.models.fact import PARTY_FACT_FORBIDDEN_KEYS


def _normalize_key(key: str) -> str:
    return (key or "").strip().lower().replace(" ", "_")


def refuse_forbidden_fact_key(key: str) -> None:
    normalized = _normalize_key(key)
    if not normalized:
        raise ValueError("PartyFact key is required.")
    if normalized in PARTY_FACT_FORBIDDEN_KEYS:
        raise ValueError(
            f"PartyFact key {normalized!r} is forbidden "
            "(fiscal, payment, or secret material)."
        )
    # Prefix / substring guards for common fiscal abbreviations.
    for token in ("codice_fiscale", "partita_iva", "iban", "access_token"):
        if token in normalized:
            raise ValueError(
                f"PartyFact key {normalized!r} is forbidden "
                "(fiscal, payment, or secret material)."
            )


@transaction.atomic
def upsert_party_fact(
    party: Party,
    *,
    key: str,
    value: str,
    source: str = "",
    trust: int = 50,
    valid_from: Optional[datetime] = None,
    valid_to: Optional[datetime] = None,
) -> PartyFact:
    """Create or refresh an open PartyFact for (party, key, source)."""
    refuse_forbidden_fact_key(key)
    key_n = _normalize_key(key)
    src = (source or "").strip()
    when = valid_from or dj_timezone.now()
    existing = (
        PartyFact.objects.filter(
            party=party, key=key_n, source=src, valid_to__isnull=True
        )
        .order_by("-valid_from")
        .first()
    )
    if existing:
        if valid_to is not None:
            existing.valid_to = valid_to
            existing.save(update_fields=["valid_to"])
            return existing
        existing.value = value if value is not None else existing.value
        if trust > existing.trust:
            existing.trust = trust
        existing.save(update_fields=["value", "trust"])
        return existing
    return PartyFact.objects.create(
        party=party,
        key=key_n,
        value=value or "",
        source=src,
        trust=trust,
        valid_from=when,
        valid_to=valid_to,
    )


@transaction.atomic
def close_party_fact(
    party: Party,
    *,
    key: str,
    source: str = "",
    closed_at: Optional[datetime] = None,
) -> Optional[PartyFact]:
    """Set valid_to on the open fact (historical / obsolete)."""
    key_n = _normalize_key(key)
    src = (source or "").strip()
    row = PartyFact.objects.filter(
        party=party, key=key_n, source=src, valid_to__isnull=True
    ).first()
    if not row:
        return None
    row.valid_to = closed_at or dj_timezone.now()
    row.save(update_fields=["valid_to"])
    return row
