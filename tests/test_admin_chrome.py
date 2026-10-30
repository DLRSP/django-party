"""Admin CRM chrome uses Contatti vocabulary (not Parties)."""
from django.contrib.admin.sites import site

from party.apps import PartyConfig
from party.models import Party


def test_app_config_verbose_name_contatti():
    assert "Contatti" in str(PartyConfig.verbose_name)


def test_party_model_verbose_names_contatti():
    assert "Contatto" in str(Party._meta.verbose_name)
    assert "Contatti" in str(Party._meta.verbose_name_plural)


def test_party_registered_in_admin():
    assert Party in site._registry
