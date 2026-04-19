from abc import ABC
from enum import Enum
from typing import ClassVar

from django_dto_field.exceptions import DtoFeatureError


class DtoCodeEnum(bytes, Enum):
    """Enum for builtin DTO codes."""

    DICT = b"\x01"


class BaseDtoFeature(ABC):
    """Abstract class for DTO features (like serializers, validators etc)."""

    dto_code: ClassVar[bytes | None] = None

    def _get_dto_code(self) -> bytes:
        if self.dto_code is None:
            raise DtoFeatureError(
                "Dto Feature Error: missing definition of `dto_code`."
            )
        return self.dto_code
