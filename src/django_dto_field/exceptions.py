class BaseDjangoDtoFieldException(Exception):
    """Base exception for django-dto-field."""


class UnknownDtoType(BaseDjangoDtoFieldException):
    """When dto type is unknown."""


class NoSerializerCode(BaseDjangoDtoFieldException):
    """When serializer has no serializer code."""


class WrongSerializerForGivenType(BaseDjangoDtoFieldException):
    """When serializer code from raw dto is different from using serializer."""


class CorruptedDtoError(BaseDjangoDtoFieldException):
    """When raw DTO binary is not valid or broken."""
