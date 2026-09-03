from django_dto_field.exceptions import BaseDjangoDTOFieldError


class DTOError(BaseDjangoDTOFieldError):
    """Error on `dto_code` attribute."""

    default_message = "Error on DTO object."


class DTOValidationError(BaseDjangoDTOFieldError):
    """Error on DTO validation."""

    default_message = "Validation error on DTO object."


class DTOSerializeError(BaseDjangoDTOFieldError):
    """Error on DTO serialization."""

    default_message = "Serialization error on DTO object."
