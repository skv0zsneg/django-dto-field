from django.db import models
from django.db.models.fields.json import JSONField

from django_dto_field.dto_field import DtoField


class ModelForTest(models.Model):
    default_json_field = JSONField(null=True)
    dict_dto_field = DtoField()
    none_dto_field = DtoField(null=True)
