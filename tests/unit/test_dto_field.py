from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError

from django_dto_field.dto_field import DTOField


@dataclass
class User:
    identifier: int


def test_field_deconstruct_and_none_values() -> None:
    field = DTOField(schema=User, null=True)
    name, path, args, kwargs = field.deconstruct()
    assert name is None
    assert path == "django_dto_field.dto_field.DTOField"
    assert args == []
    assert kwargs["schema"] is User
    assert field.to_python(None) is None
    assert field.from_db_value(None) is None
    assert field.get_db_prep_value(None) is None


def test_field_deconstruct_omits_none_schema_and_delegates_conversion() -> None:
    field = DTOField()
    assert "schema" not in field.deconstruct()[3]
    handler = MagicMock()
    handler.deserialize.return_value = {"restored": True}
    handler.serialize.return_value = b"encoded"
    field._dto_handler = handler
    value = {"value": 1}
    assert field.to_python(value) is value
    assert field.from_db_value(b"raw") == {"restored": True}
    assert field.get_db_prep_value(value) == b"encoded"
    handler.deserialize.assert_called_once_with(b"raw", None)
    handler.serialize.assert_called_once_with(value)


def test_field_validates_schema_before_returning_value() -> None:
    field = DTOField(schema=User)
    handler = MagicMock()
    field._dto_handler = handler
    value = User(1)
    assert field.to_python(value) is value
    handler.is_valid.assert_called_once_with(value, User)
    handler.is_valid.return_value = False
    with pytest.raises(ValidationError, match="not valid"):
        field.to_python(object())
