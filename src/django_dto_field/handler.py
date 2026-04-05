from typing import Generic, TypeVar

from django_dto_field.exceptions import UnknownDtoType
from django_dto_field.parser import RawDtoParser
from django_dto_field.registry import registry
from django_dto_field.serializer import BaseDtoSerializer, DictDtoSerializer

T_DTO = TypeVar("T_DTO")


class DtoHandler(Generic[T_DTO]):
    """Handler for DTO objects."""

    def serialize(self, value_dto: T_DTO) -> bytes:
        serializer = self._get_serializer_from_python(value_dto)
        return serializer.serialize(value_dto)

    def deserialize(self, raw_dto: bytes) -> T_DTO | None:
        serializer = self._get_serializer_from_raw(raw_dto)
        return serializer.deserialize(raw_dto)

    def _get_serializer_from_python(self, value_dto: T_DTO) -> BaseDtoSerializer:
        if isinstance(value_dto, dict):
            return DictDtoSerializer()
        raise UnknownDtoType()

    def _get_serializer_from_raw(self, raw_dto: bytes) -> BaseDtoSerializer:
        code = RawDtoParser.get_serializer_code(raw_dto)
        try:
            return registry.get_serializer(code)()
        except KeyError:
            raise UnknownDtoType()
