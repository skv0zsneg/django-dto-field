class BaseDjangoDtoFieldException(Exception):
    """Base exception for django-dto-field."""


class DtoHandlerError(BaseDjangoDtoFieldException):
    """Error in DTO handler."""


class SerializerError(BaseDjangoDtoFieldException):
    """Serializer DTO error."""


class CorruptedDtoError(BaseDjangoDtoFieldException):
    """Corrupted error form DTO raw object."""


class RegistryError(BaseDjangoDtoFieldException):
    """Error in global registry."""


class DtoFeatureError(BaseDjangoDtoFieldException):
    """Error with DTO feature."""
