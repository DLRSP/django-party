"""Enqueue Party field changes for adapter drain."""
from __future__ import annotations

from typing import Optional

from django.db import transaction

from party.models import Party, PartyOutbox


@transaction.atomic
def enqueue_party_change(
    party: Party,
    *,
    field: str,
    new_value: str,
    old_value: str = "",
    target: str = "beddy",
) -> PartyOutbox:
    field = (field or "").strip()
    if not field:
        raise ValueError("Outbox field is required.")
    return PartyOutbox.objects.create(
        party=party,
        target=target or "beddy",
        field=field,
        old_value=old_value or "",
        new_value=new_value if new_value is not None else "",
        status=PartyOutbox.Status.PENDING,
    )


def pending_outbox(
    *,
    target: str = "beddy",
    limit: int = 50,
):
    qs = PartyOutbox.objects.filter(
        status=PartyOutbox.Status.PENDING, target=target
    ).select_related("party").order_by("created_at")
    if limit:
        qs = qs[:limit]
    return list(qs)


@transaction.atomic
def mark_outbox(
    entry: PartyOutbox,
    *,
    status: str,
    error: str = "",
) -> PartyOutbox:
    from django.utils import timezone as dj_timezone

    entry.status = status
    entry.attempts = (entry.attempts or 0) + 1
    entry.last_error = (error or "")[:2000]
    if status in (
        PartyOutbox.Status.SENT,
        PartyOutbox.Status.SKIPPED,
        PartyOutbox.Status.FAILED,
    ):
        entry.processed_at = dj_timezone.now()
    entry.save(
        update_fields=["status", "attempts", "last_error", "processed_at"]
    )
    return entry
