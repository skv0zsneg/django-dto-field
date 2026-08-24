from typing import Any, ClassVar, final

import msgspec

from django_dto_field.dto.base import BaseDTO


@final
class DictDTO(BaseDTO[dict]):
    """Implementation DTO for `dict` type."""

    dto_code: ClassVar[int] = 1
    dto_type: ClassVar[type] = dict

    def serialize(self, value_dto: dict) -> bytes:
        return msgspec.json.encode(value_dto)

    def deserialize(self, raw_dto: bytes) -> dict:
        return msgspec.json.decode(raw_dto)

    def validate(self, value_dto: dict, schema: Any) -> None:
        # There is no builtin validation for dict type.
        ...
