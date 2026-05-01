from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
from inspect import isclass
from typing import TYPE_CHECKING, Generic, TypeVar

import msgspec

from django_dto_field.exceptions import SerializerError
from django_dto_field.features.base import BaseDtoFeature, DtoCodeEnum
from django_dto_field.parser import RawDtoParser

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

T_DTO = TypeVar("T_DTO")


class BaseDtoSerializer(BaseDtoFeature, Generic[T_DTO], ABC):
    """Interface for DTO serializer adapters."""

    def __init__(self, schema: type[T_DTO] | None = None) -> None:
        super().__init__()
        self._parser = RawDtoParser()
        self._schema = schema

    @abstractmethod
    def serialize_payload(self, value_dto: T_DTO) -> bytes:
        """Must implement payload serialize in child serializers."""

    @abstractmethod
    def deserialize_payload(self, raw_dto: bytes) -> T_DTO:
        """Must implement payload deserialize in child serializers."""

    def serialize(self, value_dto: T_DTO) -> bytes:
        payload = self.serialize_payload(value_dto)
        return self._parser.to_raw(self._get_dto_code(), payload)

    def deserialize(self, raw_dto: bytes | None) -> T_DTO | None:
        if raw_dto is None:
            return None

        current_serializer_code = self._get_dto_code()
        from_raw_serializer_code = self._parser.get_serializer_code(raw_dto)
        if from_raw_serializer_code != current_serializer_code:
            raise SerializerError(
                "Serialize Code Error: expected '%r' got '%r'"
                % (current_serializer_code, from_raw_serializer_code)
            )

        return self.deserialize_payload(self._parser.from_raw(raw_dto))


class DictDtoSerializer(BaseDtoSerializer):
    """Adapter serializer for `dict` DTO."""

    dto_code = DtoCodeEnum.DICT

    def serialize_payload(self, value_dto: dict) -> bytes:
        return msgspec.json.encode(value_dto)

    def deserialize_payload(self, raw_dto: bytes) -> dict:
        return msgspec.json.decode(raw_dto)


class DataclassDtoSerializer(BaseDtoSerializer):
    """Adapter serializer for `dataclasses.dataclass` DTO."""

    dto_code = DtoCodeEnum.DATACLASS

    def serialize_payload(self, value_dto: "DataclassInstance") -> bytes:
        return msgspec.json.encode(asdict(value_dto))

    def deserialize_payload(self, raw_dto: bytes) -> "DataclassInstance":
        if self._schema is None:
            raise SerializerError(
                "Serializer Error: for `dataclass` DTO schema must be provided"
            )
        if not is_dataclass(self._schema) and not isclass(self._schema):
            raise SerializerError(
                "Serializer Error: given wrong schema for `dataclass` DTO. "
                "Expected dataclass class but given '%s'" % self._schema
            )

        dict_inner = msgspec.json.decode(raw_dto)
        return self._schema(**dict_inner)
