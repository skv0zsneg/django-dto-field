from django.db import models
from django.db.models.fields.json import JSONField

from django_dto_field.dto_field import DTOField


class ModelForTest(models.Model):
    default_json_field = JSONField(null=True)
    dict_dto_field = DTOField()
    none_dto_field = DTOField(null=True)
