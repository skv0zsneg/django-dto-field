import dict_field.models
from django.db import migrations, models
import django_dto_field.dto_field


class Migration(migrations.Migration):
    dependencies = [("dict_field", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="DefaultDictModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "payload",
                    django_dto_field.dto_field.DTOField(
                        default=dict_field.models.default_payload
                    ),
                ),
            ],
        ),
    ]
