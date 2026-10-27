"""ContactPoint upsert with open-interval uniqueness per channel+value."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.db import transaction
from django.utils import timezone as dj_timezone

from party.models import ContactPoint, Party, PostalAddress


@transaction.atomic
def upsert_contact_point(
    party: Party,
    *,
    channel: str,
    value: str,
    use: str = ContactPoint.Use.OTHER,
    is_primary: bool = False,
    trust: int = 50,
    valid_from: Optional[datetime] = None,
) -> ContactPoint:
    value = (value or "").strip()
    if not value:
        raise ValueError("Contact point value is required.")
    when = valid_from or dj_timezone.now()
    existing = ContactPoint.objects.filter(
        party=party,
        channel=channel,
        value=value,
        valid_to__isnull=True,
    ).first()
    if existing:
        changed = False
        if is_primary and not existing.is_primary:
            ContactPoint.objects.filter(
                party=party, channel=channel, is_primary=True, valid_to__isnull=True
            ).exclude(pk=existing.pk).update(is_primary=False)
            existing.is_primary = True
            changed = True
        if trust > existing.trust:
            existing.trust = trust
            changed = True
        if use and existing.use != use:
            existing.use = use
            changed = True
        if changed:
            existing.save()
        return existing
    if is_primary:
        ContactPoint.objects.filter(
            party=party, channel=channel, is_primary=True, valid_to__isnull=True
        ).update(is_primary=False)
    return ContactPoint.objects.create(
        party=party,
        channel=channel,
        value=value,
        use=use or ContactPoint.Use.OTHER,
        is_primary=is_primary,
        trust=trust,
        valid_from=when,
    )


@transaction.atomic
def upsert_postal_address(
    party: Party,
    *,
    line1: str = "",
    line2: str = "",
    city: str = "",
    postal_code: str = "",
    region: str = "",
    country: str = "",
    use: str = "",
    valid_from: Optional[datetime] = None,
) -> PostalAddress:
    when = valid_from or dj_timezone.now()
    line1 = (line1 or "").strip()
    city = (city or "").strip()
    postal_code = (postal_code or "").strip()
    country = (country or "").strip().upper()[:2]
    existing = PostalAddress.objects.filter(
        party=party,
        line1=line1,
        city=city,
        postal_code=postal_code,
        country=country,
        valid_to__isnull=True,
    ).first()
    if existing:
        return existing
    return PostalAddress.objects.create(
        party=party,
        line1=line1,
        line2=(line2 or "").strip(),
        city=city,
        postal_code=postal_code,
        region=(region or "").strip(),
        country=country,
        use=use or "",
        valid_from=when,
    )
