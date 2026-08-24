from typing import ClassVar


class BaseDjangoDTOFieldError(Exception):
    """Base exception for django-dto-field."""

    default_message: ClassVar[str] = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class DtoHandlerError(BaseDjangoDTOFieldError):
    """Error in DTO handler."""


class SerializerError(BaseDjangoDTOFieldError):
    """Serializer DTO error."""


class BinaryDTOParserError(BaseDjangoDTOFieldError):
    """Base error for binary DTO parser."""

    default_message = "Error on binary DTO parser"


class RegistryError(BaseDjangoDTOFieldError):
    """Error in global registry."""


class DtoFeatureError(BaseDjangoDTOFieldError):
    """Error with DTO feature."""


class ValidatorError(BaseDjangoDTOFieldError):
    """Error with DTO validator."""
