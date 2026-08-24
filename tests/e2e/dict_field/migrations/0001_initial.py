import dict_field.models
from django.db import migrations, models
import django_dto_field.dto_field


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="DictModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payload", django_dto_field.dto_field.DTOField()),
            ],
        ),
        migrations.CreateModel(
            name="DataclassModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payload", django_dto_field.dto_field.DTOField(schema=dict_field.models.UserDTO)),
            ],
        ),
        migrations.CreateModel(
            name="NullableModel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payload", django_dto_field.dto_field.DTOField(blank=True, null=True, schema=dict_field.models.UserDTO)),
            ],
        ),
    ]
