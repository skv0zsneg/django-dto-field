from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import msgspec

T_DTO = TypeVar("T_DTO")


class BaseDtoSerializer(Generic[T_DTO], ABC):
    """Interface for DTO serializer adapters."""

    @abstractmethod
    def serialize(self, value_dto: T_DTO) -> bytes: ...

    @abstractmethod
    def deserialize(self, raw_dto: bytes) -> T_DTO: ...


class DictDtoSerializer(BaseDtoSerializer):
    """Adapter serializer for `dict` DTO."""

    def serialize(self, value_dto: dict) -> bytes:
        return msgspec.json.encode(value_dto)

    def deserialize(self, raw_dto: bytes) -> dict:
        return msgspec.json.decode(raw_dto)
