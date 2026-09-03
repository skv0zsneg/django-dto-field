from typing import Generic, cast

from django_dto_field.dto.base import T_DTO, DTORegistry
from django_dto_field.dto.exceptions import DTOSerializeError, DTOValidationError
from django_dto_field.parser import BinaryDTOParser


class HandlerDTO(Generic[T_DTO]):
    """Handler for DTO objects."""

    _dto_registry: DTORegistry = DTORegistry()

    def serialize(self, value_dto: T_DTO) -> bytes:
        """Serializer DTO value."""
        dto_object = self._dto_registry.get_from_type(type(value_dto))
        if dto_object is None:
            raise DTOSerializeError(f"No DTO found for type: {type(value_dto)}")
        dto_instance = dto_object()
        parser = BinaryDTOParser()
        return parser.pack(dto_object.dto_code, dto_instance.serialize(value_dto))

    def deserialize(self, raw_dto: bytes, schema: type[T_DTO] | None) -> T_DTO:
        """Deserialize into DTO object."""
        parser = BinaryDTOParser()
        unpacked_dto_code, payload = parser.unpack(raw_dto)

        dto_object = self._dto_registry.get_from_code(unpacked_dto_code)
        if dto_object is None:
            raise DTOSerializeError(f"No DTO found for code: {unpacked_dto_code}")
        dto_instance = dto_object()

        return cast(T_DTO, dto_instance.deserialize(payload))

    def is_valid(self, value_dto: T_DTO, schema: type[T_DTO] | None = None) -> bool:
        """Validate DTO value."""
        dto_object = self._dto_registry.get_from_type(type(value_dto))
        if dto_object is None:
            raise DTOSerializeError(f"No DTO found for type: {type(value_dto)}")
        dto_instance = dto_object()
        try:
            if schema is None:
                dto_instance.validate(value_dto)
            else:
                dto_instance.validate(value_dto, schema)
        except DTOValidationError:
            return False
        return True
