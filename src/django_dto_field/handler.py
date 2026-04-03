from typing import Generic, TypeVar

from django_dto_field.exceptions import UnexpectedEmptySerializerHandler, UnknownDtoType
from django_dto_field.serializer import BaseDtoSerializer, DictDtoSerializer

T_DTO = TypeVar("T_DTO")


class DtoHandler(Generic[T_DTO]):
    """Handler for DTO objects."""

    def __init__(self) -> None:
        self._serializer: BaseDtoSerializer | None = None

    def serialize(self, value_dto: T_DTO) -> bytes:
        if self._serializer is None:
            return self._get_serializer(value_dto).serialize(value_dto)
        return self._serializer.serialize(value_dto)

    def deserialize(self, raw_dto: bytes) -> T_DTO:
        if self._serializer is None:
            raise UnexpectedEmptySerializerHandler()
        return self._serializer.deserialize(raw_dto)

    def _get_serializer(self, value_dto: T_DTO) -> BaseDtoSerializer:
        if self._serializer is not None:
            return self._serializer

        if isinstance(value_dto, dict):
            self._serializer = DictDtoSerializer()
        else:
            raise UnknownDtoType()

        return self._serializer
