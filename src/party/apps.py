from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PartyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "party"
    label = "party"
    # Staff Admin chrome: Contatti (CRM). Model identifiers stay English.
    verbose_name = _("Contatti")

    def ready(self) -> None:
        from party.rbac import connect_rbac_signals

        connect_rbac_signals()
