from django.core.exceptions import ValidationError
from django.db.models.fields import BinaryField

from django_dict_field.serializer import Serializer


class DictField(BinaryField):
    """Storing a set of params in one field."""

    def __init__(self, *args, **kwargs) -> None:
        self.serializer = Serializer()
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value: bytes | None, *args, **kwargs) -> dict | None:
        if value is None:
            return value
        return self.serializer.deserialize(value)

    def to_python(self, value: dict) -> dict:
        if not isinstance(value, dict):
            raise ValidationError(f"Given value '{value}' must be 'dict' instance!")
        return value

    def get_db_prep_value(self, value: dict | None, *args, **kwargs) -> bytes | None:
        if value is None:
            return value
        return self.serializer.serialize(value)

    def value_to_string(self, obj):
        return str(self.value_from_object(obj))
