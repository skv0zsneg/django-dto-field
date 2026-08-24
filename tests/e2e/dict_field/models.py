from dataclasses import dataclass

from django.db import models

from django_dto_field.dto_field import DTOField


@dataclass
class UserDTO:
    identifier: int
    email: str
    active: bool = True


class DictModel(models.Model):
    payload = DTOField()


class DataclassModel(models.Model):
    payload = DTOField(schema=UserDTO)


class NullableModel(models.Model):
    payload = DTOField(schema=UserDTO, null=True, blank=True)
