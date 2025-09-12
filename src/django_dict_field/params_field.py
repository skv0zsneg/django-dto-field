from typing import Any, Generic, Optional

from django.core.exceptions import ValidationError
from django.db.models.fields import BinaryField

from django_params_field.serializer import P, Serializer


class ParamsField(BinaryField, Generic[P]):
    """Storing a set of params in one field."""

    def __init__(self, params_type: Optional[P] = None, *args, **kwargs) -> None:
        self.params_type = params_type
        self.serializer = Serializer(self.params_type)
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple[Any, Any, Any, Any]:
        name, path, args, kwargs = super().deconstruct()
        kwargs["params_type"] = self.params_type
        return name, path, args, kwargs

    def from_db_value(self, value: bytes, *args, **kwargs) -> P:
        return self.serializer.deserialize(value)

    def to_python(self, value: P) -> P:
        return value

    def get_db_prep_value(self, value: P, *args, **kwargs) -> bytes:
        return self.serializer.serialize(value)

    def validate(self, value: P, *args, **kwargs) -> None:
        if not self.serializer.is_valid(value):
            raise ValidationError(f"Given value '{value}' is not valid!")
