from typing import TypeVar

from django_dto_field.exceptions import DtoHandlerError
from django_dto_field.features.base import DtoCodeEnum
from django_dto_field.features.serializers import BaseDtoSerializer, DictDtoSerializer
from django_dto_field.parser import RawDtoParser

T_DTO = TypeVar("T_DTO")


class DtoHandler[T_DTO]:
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
        raise DtoHandlerError(
            "DtoHandlerError: no serializer for DTO value '%s'" % str(value_dto)
        )

    def _get_serializer_from_raw(self, raw_dto: bytes) -> BaseDtoSerializer:
        code = RawDtoParser.get_serializer_code(raw_dto)
        code_to_serializer: dict[bytes, type[BaseDtoSerializer]] = {
            DtoCodeEnum.DICT: DictDtoSerializer,
        }
        try:
            return code_to_serializer[code]()
        except KeyError:
            raise DtoHandlerError(
                "DTO Handler Error: no serializer for DTO value %r" % raw_dto
            )
