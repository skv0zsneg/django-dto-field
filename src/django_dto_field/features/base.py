from abc import ABC
from enum import Enum
from typing import ClassVar, Self

from django_dto_field.exceptions import DtoFeatureError


class DtoCodeEnum(bytes, Enum):
    """Enum for builtin DTO codes."""

    DICT = b"\x01"


class BaseDtoFeature(ABC):
    """Abstract class for DTO features (like serializers, validators etc)."""

    dto_code: ClassVar[bytes | None] = None

    def __new__(cls) -> Self:
        cls._get_dto_code()  # <-- calling just to be sure that dto_code is set.
        return super().__new__(cls)

    @classmethod
    def _get_dto_code(cls) -> bytes:
        if cls.dto_code is None:
            raise DtoFeatureError(
                "Dto Feature Error: missing definition of `dto_code`."
            )
        return cls.dto_code
