from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from django_dto_field.exceptions import ValidatorError
from django_dto_field.features.base import BaseDtoFeature, DtoCodeEnum

T_DTO = TypeVar("T_DTO")


class BaseDtoValidator(BaseDtoFeature, Generic[T_DTO], ABC):
    """Interface for DTO validators."""

    @abstractmethod
    def validate(self, value_dto: T_DTO, schema: type[T_DTO]) -> None:
        """Must implement validate method in child validators."""


class DataclassValidator(BaseDtoValidator):
    """Validator for `dataclass`."""

    dto_code = DtoCodeEnum.DATACLASS

    def validate(self, value_dto: T_DTO, schema: type[T_DTO]) -> None:
        if not isinstance(value_dto, schema):
            raise ValidatorError(
                "Validation Error: given dataclass DTO is not match given schema %s"
                % schema
            )
