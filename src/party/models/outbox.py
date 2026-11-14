"""Outbound change log — Party mutations awaiting adapter drain (e.g. Beddy)."""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from party.models.party import Party


class PartyOutbox(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")
        SKIPPED = "skipped", _("Skipped")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(
        Party, on_delete=models.CASCADE, related_name="outbox_entries"
    )
    target = models.CharField(
        max_length=32,
        default="beddy",
        db_index=True,
        help_text=_("Adapter namespace (beddy, …)."),
    )
    field = models.CharField(max_length=64)
    old_value = models.TextField(blank=True, default="")
    new_value = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("party outbox entry")
        verbose_name_plural = _("party outbox entries")
        indexes = [
            models.Index(fields=["status", "target", "created_at"]),
            models.Index(fields=["party", "status"]),
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.target}:{self.field}@{self.party_id} ({self.status})"
