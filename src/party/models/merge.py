"""Audit trail for party merges (HITL)."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from party.models.party import Party


class PartyMergeEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survivor = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="merge_events_as_survivor"
    )
    merged = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="merge_events_as_merged"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("party merge event")
        verbose_name_plural = _("party merge events")

    def __str__(self) -> str:
        return f"merge {self.merged_id} → {self.survivor_id}"
