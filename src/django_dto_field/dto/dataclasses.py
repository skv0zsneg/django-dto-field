from dataclasses import asdict, is_dataclass
from inspect import isclass
from typing import TYPE_CHECKING, ClassVar, final

import msgspec

from django_dto_field.dto.base import BaseDTO
from django_dto_field.dto.exceptions import DTOValidationError

if TYPE_CHECKING:  # pragma: no cover
    from _typeshed import DataclassInstance

# NOTE: Python don't have type for dataclasses object. Define a placeholder.
_DataclassInstance: type = object


@final
class DataclassDTO(BaseDTO["DataclassInstance"]):
    """Implementation DTO for `dataclass` type."""

    dto_code: ClassVar[int] = 2
    dto_type: ClassVar[type["DataclassInstance"]] = _DataclassInstance

    def serialize(self, value_dto: "DataclassInstance") -> bytes:
        return msgspec.json.encode(asdict(value_dto))

    def deserialize(self, raw_dto: bytes) -> "DataclassInstance":
        if self._schema is None:
            raise DTOValidationError("For `dataclass` DTO schema must be provided")

        if not is_dataclass(self._schema) and not isclass(self._schema):
            raise DTOValidationError(
                f"Given wrong schema for `dataclass` DTO. "
                f"Expected dataclass class but given '{self._schema}'"
            )

        dict_inner = msgspec.json.decode(raw_dto)
        return self._schema(**dict_inner)

    def validate(
        self,
        value_dto: "DataclassInstance",
        schema: type["DataclassInstance"],
    ) -> None:
        if not isinstance(value_dto, schema):
            raise DTOValidationError(
                f"Given dataclass DTO is not match given schema {schema}"
            )
