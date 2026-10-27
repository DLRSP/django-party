"""ExternalIdentity upsert with open-interval uniqueness."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.db import transaction
from django.utils import timezone as dj_timezone

from party.models import ExternalIdentity, Party


@transaction.atomic
def upsert_external_identity(
    party: Party,
    *,
    namespace: str,
    scheme: str,
    value: str,
    trust: int = 50,
    payload_hash: str = "",
    valid_from: Optional[datetime] = None,
) -> ExternalIdentity:
    value = str(value).strip()
    when = valid_from or dj_timezone.now()
    existing = ExternalIdentity.objects.filter(
        namespace=namespace, scheme=scheme, value=value, valid_to__isnull=True
    ).first()
    if existing:
        if existing.party_id != party.id:
            raise ValueError(
                f"External identity {namespace}:{scheme}={value} already "
                f"bound to another party."
            )
        if trust > existing.trust:
            existing.trust = trust
        if payload_hash:
            existing.payload_hash = payload_hash
        existing.save(update_fields=["trust", "payload_hash"])
        return existing
    return ExternalIdentity.objects.create(
        party=party,
        namespace=namespace,
        scheme=scheme,
        value=value,
        trust=trust,
        payload_hash=payload_hash or "",
        valid_from=when,
    )
