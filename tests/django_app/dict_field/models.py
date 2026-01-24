from django.db import models
from django.db.models.fields.json import JSONField

from django_dict_field import DictField


class ModelForTest(models.Model):
    default_json_field = JSONField(null=True)
    default_dict_field = DictField()
