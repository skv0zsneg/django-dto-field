from collections.abc import Sequence
from typing import Any, Generic

from django.core.exceptions import ValidationError
from django.db.models.fields import BinaryField

from django_dto_field.dto.base import T_DTO
from django_dto_field.handler import HandlerDTO


class DTOField(BinaryField, Generic[T_DTO]):
    """DTO Field for efficient storing structures in DB."""

    empty_strings_allowed = False

    def __init__(
        self,
        *args,
        schema: type[T_DTO] | None = None,
        **kwargs,
    ) -> None:
        self._dto_handler: HandlerDTO = HandlerDTO()
        self._schema = schema
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple[str, str, Sequence[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        if self._schema is not None:
            kwargs["schema"] = self._schema
        return name, path, args, kwargs

    def to_python(
        self,
        value: T_DTO | None,  # noqa: WPS110
    ) -> T_DTO | None:
        if value is None:
            return value
        if self._schema:
            if not self._dto_handler.is_valid(value, self._schema):
                raise ValidationError(
                    "given value '%s' is not valid for schema '%s'"
                    % (value, self._schema)
                )
        return value

    def from_db_value(
        self,
        value: bytes | None,  # noqa: WPS110
        *args,
        **kwargs,
    ) -> T_DTO | None:
        if value is None:
            return value
        return self._dto_handler.deserialize(value, self._schema)

    def get_db_prep_value(
        self,
        value: T_DTO | None,  # noqa: WPS110
        *args,
        **kwargs,
    ) -> bytes | None:
        if value is None:
            return value
        return self._dto_handler.serialize(value)
