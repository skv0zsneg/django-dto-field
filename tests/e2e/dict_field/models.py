import dataclasses
from django.db import models
from django_dto_field.dto_field import DTOField


@dataclasses.dataclass
class UserDTO:
    id: int
    email: str
    is_active: bool = True


class DictModel(models.Model):
    payload = DTOField()


class DataclassModel(models.Model):
    payload = DTOField(schema=UserDTO)


class NullableSchemaModel(models.Model):
    payload = DTOField(schema=UserDTO, null=True, blank=True)
