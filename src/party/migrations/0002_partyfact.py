import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("party", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PartyFact",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("key", models.CharField(db_index=True, max_length=128)),
                ("value", models.TextField(blank=True, default="")),
                ("source", models.CharField(blank=True, default="", max_length=64)),
                ("trust", models.PositiveSmallIntegerField(default=50)),
                ("valid_from", models.DateTimeField()),
                ("valid_to", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="facts",
                        to="party.party",
                    ),
                ),
            ],
            options={
                "verbose_name": "party fact",
                "verbose_name_plural": "party facts",
            },
        ),
        migrations.AddIndex(
            model_name="partyfact",
            index=models.Index(
                fields=["party", "key"], name="party_party_party_i_7a1f01_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="partyfact",
            index=models.Index(
                fields=["key", "source"], name="party_party_key_8c2e11_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="partyfact",
            constraint=models.UniqueConstraint(
                condition=models.Q(("valid_to__isnull", True)),
                fields=("party", "key", "source"),
                name="party_fact_open_unique",
            ),
        ),
    ]
