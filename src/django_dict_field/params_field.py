from typing import Any

from django.core.exceptions import ValidationError
from django.db.models.fields import BinaryField

from django_dict_field.serializer import Serializer


class DictField(BinaryField):
    """Storing a set of params in one field."""

    def __init__(self, *args, **kwargs) -> None:
        self.serializer = Serializer()
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple[Any, Any, Any, Any]:
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def from_db_value(self, value: bytes, *args, **kwargs) -> dict:
        return self.serializer.deserialize(value)

    def to_python(self, value: dict) -> dict:
        if not isinstance(value, dict):
            raise ValidationError(f"Given value '{value}' must be 'dict' instance!")
        return value

    def get_db_prep_value(self, value: dict, *args, **kwargs) -> bytes:
        if value is not None:
            return self.serializer.serialize(value)
        return value

    def value_to_string(self, obj):
        return str(self.value_from_object(obj))
