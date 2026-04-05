from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar

import msgspec

from django_dto_field.exceptions import SerializerError
from django_dto_field.parser import RawDtoParser
from django_dto_field.registry import registry

T_DTO = TypeVar("T_DTO")


class BaseDtoSerializer(Generic[T_DTO], ABC):
    """Interface for DTO serializer adapters."""

    serializer_code: ClassVar[bytes | None] = None

    def __init__(self) -> None:
        registry.save_serializer(
            self._get_serializer_code(),
            self.__class__,
        )
        self._parser = RawDtoParser()

    def serialize(self, value_dto: T_DTO) -> bytes:
        payload = self.serialize_payload(value_dto)
        return self._parser.to_raw(self._get_serializer_code(), payload)

    def deserialize(self, raw_dto: bytes | None) -> T_DTO | None:
        if raw_dto is None:
            return None

        current_serializer_code = self._get_serializer_code()
        from_raw_serializer_code = self._parser.get_serializer_code(raw_dto)
        if from_raw_serializer_code != current_serializer_code:
            raise SerializerError(
                "Serialize Code Error: expected '%s' got '%s'"
                % (current_serializer_code, from_raw_serializer_code)
            )

        return self.deserialize_payload(self._parser.from_raw(raw_dto))

    def _get_serializer_code(self) -> bytes:
        if self.serializer_code is None:
            raise SerializerError("Serialize Code Error: must be defined.")
        return self.serializer_code

    @abstractmethod
    def serialize_payload(self, value_dto: T_DTO) -> bytes:
        """Must implement payload serialize in child serializers."""

    @abstractmethod
    def deserialize_payload(self, raw_dto: bytes) -> T_DTO:
        """Must implement payload deserialize in child serializers."""


class DictDtoSerializer(BaseDtoSerializer):
    """Adapter serializer for `dict` DTO."""

    serializer_code = b"\x01"

    def serialize_payload(self, value_dto: dict) -> bytes:
        return msgspec.json.encode(value_dto)

    def deserialize_payload(self, raw_dto: bytes) -> dict:
        return msgspec.json.decode(raw_dto)
