from typing import Optional

from django.core.exceptions import ValidationError
from django.db.models.fields import BinaryField

from django_dict_field.serializer import Serializer


class DictField(BinaryField):
    """Storing a set of params in one field."""

    def __init__(
        self,
        schema: dict | None = None,
        strict_schema_validation: bool = False,
        *args,
        **kwargs,
    ) -> None:
        self._schema = schema
        self._strict_schema_validation = strict_schema_validation
        self._serializer = Serializer()
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self._schema is not None:
            kwargs["schema"] = self._schema
        if self._strict_schema_validation is not False:
            kwargs["strict_schema_validation"] = self._strict_schema_validation
        return name, path, args, kwargs

    def from_db_value(self, value: Optional[bytes], *args, **kwargs) -> Optional[dict]:
        if value is None:
            return value
        return self._serializer.deserialize(value)

    def to_python(self, value: dict) -> dict:
        if not isinstance(value, dict):
            raise ValidationError(f"Given value '{value}' must be 'dict' instance!")
        return value

    def get_db_prep_value(self, value: Optional[dict], *args, **kwargs) -> Optional[bytes]:
        if value is None:
            return value
        return self._serializer.serialize(value)

    def value_to_string(self, obj):
        return str(self.value_from_object(obj))
