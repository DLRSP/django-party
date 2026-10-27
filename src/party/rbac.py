"""Idempotent feature-group seeds for CRM Contatti plane (Django Group)."""
from __future__ import annotations

import logging

from django.apps import apps
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)

# English codes only — Contatti is UX label, not a Group id.
CRM_FEATURE_GROUPS = {
    "dlrsp:crm.contacts_view": [
        ("party", "view_party"),
        ("party", "view_contactpoint"),
        ("party", "view_postaladdress"),
        ("party", "view_externalidentity"),
        ("party", "view_partyfact"),
    ],
    "dlrsp:crm.contacts_edit": [
        ("party", "view_party"),
        ("party", "change_party"),
        ("party", "add_party"),
        ("party", "view_contactpoint"),
        ("party", "change_contactpoint"),
        ("party", "add_contactpoint"),
        ("party", "view_postaladdress"),
        ("party", "change_postaladdress"),
        ("party", "add_postaladdress"),
        ("party", "view_externalidentity"),
        ("party", "change_externalidentity"),
        ("party", "add_externalidentity"),
        ("party", "view_partyfact"),
        ("party", "change_partyfact"),
        ("party", "add_partyfact"),
    ],
    "dlrsp:crm.consent_view": [
        ("party", "view_consentrecord"),
    ],
    "dlrsp:crm.account_code_hitl": [
        ("party", "view_partyaccount"),
        ("party", "change_partyaccount"),
        ("party", "add_partyaccount"),
    ],
}


def seed_crm_feature_groups(**kwargs) -> None:
    """Create CRM feature Groups and attach permissions. Never assign to users."""
    try:
        Group = apps.get_model("auth", "Group")
        Permission = apps.get_model("auth", "Permission")
    except LookupError:
        return
    for group_name, perm_specs in CRM_FEATURE_GROUPS.items():
        group, _created = Group.objects.get_or_create(name=group_name)
        perms = []
        for app_label, codename in perm_specs:
            perm = Permission.objects.filter(
                content_type__app_label=app_label, codename=codename
            ).first()
            if perm is not None:
                perms.append(perm)
            else:
                logger.debug(
                    "party rbac: skip missing permission %s.%s",
                    app_label,
                    codename,
                )
        if perms:
            group.permissions.set(perms)


def connect_rbac_signals() -> None:
    post_migrate.connect(
        seed_crm_feature_groups,
        sender=apps.get_app_config("party"),
        dispatch_uid="party.seed_crm_feature_groups",
    )
