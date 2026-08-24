from dataclasses import dataclass

from django.db import models

from django_dto_field.dto_field import DTOField


def default_payload() -> dict:
    """Return a new default value for every model instance."""
    return {"version": 1, "flags": []}


@dataclass
class UserDTO:
    identifier: int
    email: str
    active: bool = True


class DictModel(models.Model):
    payload: DTOField[dict] = DTOField()


class DataclassModel(models.Model):
    payload = DTOField(schema=UserDTO)


class NullableModel(models.Model):
    payload = DTOField(schema=UserDTO, null=True, blank=True)


class DefaultDictModel(models.Model):
    payload: DTOField[dict] = DTOField(default=default_payload)
