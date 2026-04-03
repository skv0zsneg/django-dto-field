class BaseDjangoDtoFieldException(Exception):
    """Base exception for django-dto-field."""


class UnexpectedEmptySerializerHandler(BaseDjangoDtoFieldException):
    """When deserialize is called but serializer handler still unknown."""


class UnknownDtoType(BaseDjangoDtoFieldException):
    """When dto type is unknown."""
