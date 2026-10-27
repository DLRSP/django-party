"""PartyAccount helpers — no posting / balances."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone as dj_timezone

from party.models import Party, PartyAccount


def _now() -> datetime:
    return dj_timezone.now()


@transaction.atomic
def upsert_party_account(
    party: Party,
    *,
    code: str,
    kind: str,
    label: str = "",
    is_default: bool = False,
    valid_from: Optional[datetime] = None,
) -> PartyAccount:
    code = (code or "").strip()
    if not code:
        raise ValidationError({"code": "Account code is required."})
    if code.isdigit() and len(code) >= 6:
        raise ValidationError(
            {
                "code": (
                    "Numeric identifiers from external PMS must not be used "
                    "as account codes."
                )
            }
        )
    when = valid_from or _now()
    if is_default:
        PartyAccount.objects.filter(
            party=party, kind=kind, is_default=True, valid_to__isnull=True
        ).exclude(code=code).update(is_default=False, valid_to=when)
    existing = (
        PartyAccount.objects.filter(
            party=party, code=code, valid_to__isnull=True
        )
        .order_by("-valid_from")
        .first()
    )
    if existing:
        existing.label = label or existing.label
        existing.kind = kind
        existing.is_default = is_default
        existing.status = PartyAccount.Status.ACTIVE
        existing.full_clean()
        existing.save()
        return existing
    account = PartyAccount(
        party=party,
        code=code,
        label=label,
        kind=kind,
        is_default=is_default,
        valid_from=when,
    )
    account.full_clean()
    account.save()
    return account


def get_default_party_account(
    party: Party,
    kind: str,
    *,
    as_of: Optional[datetime] = None,
) -> Optional[PartyAccount]:
    when = as_of or _now()
    qs = PartyAccount.objects.filter(
        party=party,
        kind=kind,
        status=PartyAccount.Status.ACTIVE,
        valid_from__lte=when,
    ).filter(models_q_open(when))
    return qs.filter(is_default=True).first() or qs.order_by("-valid_from").first()


def models_q_open(when: datetime):
    from django.db.models import Q

    return Q(valid_to__isnull=True) | Q(valid_to__gt=when)
