"""CRM feature-group seeds and mutate-denial contracts."""

from __future__ import annotations

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from party.admin import ConsentRecordAdmin
from party.models import ConsentRecord, Party
from party.rbac import CRM_FEATURE_GROUPS, seed_crm_feature_groups


def _seed_crm() -> None:
    create_permissions(apps.get_app_config("party"), verbosity=0)
    seed_crm_feature_groups()


@pytest.mark.django_db
def test_crm_feature_groups_seed_english_codes_only():
    _seed_crm()
    names = set(Group.objects.values_list("name", flat=True))
    for group_name in CRM_FEATURE_GROUPS:
        assert group_name in names
    assert "dlrsp:crm.contatti_view" not in names
    assert "dlrsp:crm.contatti_edit" not in names


@pytest.mark.django_db
def test_contacts_view_read_ok_mutate_denied():
    _seed_crm()
    User = get_user_model()
    user = User.objects.create_user(username="viewcrm", password="x")
    user.groups.add(Group.objects.get(name="dlrsp:crm.contacts_view"))
    user = User.objects.get(pk=user.pk)
    assert user.has_perm("party.view_party")
    assert user.has_perm("party.view_contactpoint")
    assert user.has_perm("party.view_externalidentity")
    assert user.has_perm("party.view_partyfact")
    assert not user.has_perm("party.change_party")
    assert not user.has_perm("party.add_party")
    assert not user.has_perm("party.change_contactpoint")
    assert not user.has_perm("party.add_contactpoint")


@pytest.mark.django_db
def test_contacts_edit_can_mutate_party_and_contact_point():
    _seed_crm()
    User = get_user_model()
    user = User.objects.create_user(username="editcrm", password="x")
    user.groups.add(Group.objects.get(name="dlrsp:crm.contacts_edit"))
    user = User.objects.get(pk=user.pk)
    assert user.has_perm("party.change_party")
    assert user.has_perm("party.add_contactpoint")
    assert user.has_perm("party.change_externalidentity")
    # Account-code HITL stays on a separate group.
    assert not user.has_perm("party.change_partyaccount")
    assert not user.has_perm("party.add_partyaccount")


@pytest.mark.django_db
def test_consent_view_cannot_create_consent_record():
    _seed_crm()
    User = get_user_model()
    user = User.objects.create_user(username="consentview", password="x")
    user.groups.add(Group.objects.get(name="dlrsp:crm.consent_view"))
    user = User.objects.get(pk=user.pk)
    assert user.has_perm("party.view_consentrecord")
    assert not user.has_perm("party.add_consentrecord")
    assert not user.has_perm("party.change_consentrecord")

    rf = RequestFactory()
    request = rf.get("/admin/party/consentrecord/add/")
    request.user = user
    admin = ConsentRecordAdmin(ConsentRecord, AdminSite())
    assert admin.has_add_permission(request) is False
    assert admin.has_change_permission(request) is False


@pytest.mark.django_db
def test_party_account_write_requires_account_code_hitl():
    _seed_crm()
    User = get_user_model()
    viewer = User.objects.create_user(username="noviewacct", password="x")
    viewer.groups.add(Group.objects.get(name="dlrsp:crm.contacts_edit"))
    viewer = User.objects.get(pk=viewer.pk)
    assert not viewer.has_perm("party.add_partyaccount")
    assert not viewer.has_perm("party.change_partyaccount")

    hitl = User.objects.create_user(username="hitl", password="x")
    hitl.groups.add(Group.objects.get(name="dlrsp:crm.account_code_hitl"))
    hitl = User.objects.get(pk=hitl.pk)
    assert hitl.has_perm("party.view_partyaccount")
    assert hitl.has_perm("party.add_partyaccount")
    assert hitl.has_perm("party.change_partyaccount")


@pytest.mark.django_db
def test_seed_does_not_assign_groups_to_users():
    _seed_crm()
    User = get_user_model()
    user = User.objects.create_user(username="unassigned", password="x")
    Party.objects.create(kind=Party.Kind.PERSON, given_name="A", family_name="B")
    assert user.groups.count() == 0
