from dataclasses import is_dataclass
from inspect import isclass
from typing import Any, Generic, cast

from django_dto_field.dto.base import T_DTO, BaseDTO
from django_dto_field.dto.dataclasses import DataclassDTO
from django_dto_field.dto.dict import DictDTO
from django_dto_field.dto.exceptions import DTOSerializeError, DTOValidationError
from django_dto_field.parser import BinaryDTOParser


class HandlerDTO(Generic[T_DTO]):
    """Handler for DTO objects."""

    def serialize(self, value_dto: T_DTO) -> bytes:
        """Serializer DTO value."""
        dto_object: BaseDTO[Any]
        if isinstance(value_dto, dict):
            dto_object = DictDTO()
        elif is_dataclass(value_dto) and not isclass(value_dto):
            dto_object = DataclassDTO()
        else:
            dto_object = BaseDTO.from_type(type(value_dto))()
        parser = BinaryDTOParser()
        return parser.pack(dto_object.dto_code, dto_object.serialize(value_dto))

    def deserialize(self, raw_dto: bytes, schema: type[T_DTO] | None) -> T_DTO:
        """Deserialize into DTO object."""
        parser = BinaryDTOParser()
        unpacked_dto_code, payload = parser.unpack(raw_dto)

        dto_object: BaseDTO[Any]
        if schema is dict:
            dto_object = DictDTO()
        elif isclass(schema) and is_dataclass(schema):
            dto_object = DataclassDTO(schema)
        elif schema:
            dto_object = BaseDTO.from_type(schema)()
        else:
            dto_object = BaseDTO.from_code(unpacked_dto_code)()

        if unpacked_dto_code != dto_object.dto_code:
            raise DTOSerializeError(
                "DTO code mismatch. Seems like a wrong schema or wrong unpacked payload."
            )
        return cast(T_DTO, dto_object.deserialize(payload))

    def is_valid(self, value_dto: T_DTO, schema: type[T_DTO]) -> bool:
        """Validate DTO value."""
        dto_object: BaseDTO[Any]
        if schema is dict:
            dto_object = DictDTO()
        elif isclass(schema) and is_dataclass(schema):
            dto_object = DataclassDTO()
        else:
            dto_object = BaseDTO.from_type(schema)()
        try:
            dto_object.validate(value_dto, schema)
        except DTOValidationError:
            return False
        return True
