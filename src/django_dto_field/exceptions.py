class BaseDjangoDtoFieldException(Exception):
    """Base exception for django-dto-field."""


class UnknownDtoType(BaseDjangoDtoFieldException):
    """When dto type is unknown."""


class SerializerError(BaseDjangoDtoFieldException):
    """Serializer DTO error."""


class CorruptedDtoError(BaseDjangoDtoFieldException):
    """Corrupted error form DTO raw object."""
