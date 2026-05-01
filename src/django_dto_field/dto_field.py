from typing import Generic, Optional, TypeVar

from django.db.models.fields import BinaryField

from django_dto_field.handler import DtoHandler

T_DTO = TypeVar("T_DTO")


class DTOField(BinaryField, Generic[T_DTO]):
    """DTO Field for efficient storing structures in DB."""

    empty_strings_allowed = False

    def __init__(self, *args, **kwargs) -> None:
        self._dto_handler: DtoHandler = DtoHandler()
        super().__init__(*args, **kwargs)

    def from_db_value(
        self,
        value: Optional[bytes],  # noqa: WPS110
        *args,
        **kwargs,
    ) -> Optional[T_DTO]:
        if value is None:
            return value
        return self._dto_handler.deserialize(value)

    def get_db_prep_value(
        self,
        value: Optional[T_DTO],  # noqa: WPS110
        *args,
        **kwargs,
    ) -> Optional[bytes]:
        if value is None:
            return value
        return self._dto_handler.serialize(value)
