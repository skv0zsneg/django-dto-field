from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar, final

from django_dto_field.dto.exceptions import DTOError

T_DTO = TypeVar("T_DTO")


@final
class DTORegistry(Generic[T_DTO]):
    """Registry for DTO objects."""

    def __init__(self) -> None:
        self._code_to_instances: dict[int, type["BaseDTO"]] = {}
        self._type_to_instances: dict[type[T_DTO], type["BaseDTO"]] = {}

    def register(self, dto_instance: type["BaseDTO"]) -> None:
        self._check_code_duplicates(dto_instance)
        self._check_type_duplicates(dto_instance)

        self._code_to_instances[dto_instance.dto_code] = dto_instance
        self._type_to_instances[dto_instance.dto_type] = dto_instance

    def get_from_type(self, dto_type: type[T_DTO]) -> type["BaseDTO"] | None:
        return self._type_to_instances.get(dto_type)

    def get_from_code(self, dto_code: int) -> type["BaseDTO"] | None:
        return self._code_to_instances.get(dto_code)

    def _check_code_duplicates(self, dto_instance: type["BaseDTO"]) -> None:
        existing = self._code_to_instances.get(dto_instance.dto_code)
        if existing is not None:
            raise DTOError(
                f"`dto_code` {dto_instance.dto_code} is already reserved by "
                f"'{existing.__name__}'. '{dto_instance.__name__}' cannot use it."
            )

    def _check_type_duplicates(self, dto_instance: type["BaseDTO"]) -> None:
        existing = self._type_to_instances.get(dto_instance.dto_type)
        if existing is not None:
            raise DTOError(
                f"`dto_type` {dto_instance.dto_type} is already reserved by "
                f"'{existing.__name__}'. '{dto_instance.__name__}' cannot use it."
            )


class BaseDTO(ABC, Generic[T_DTO]):  # noqa: WPS214
    """Base class for DTO objects."""

    dto_code: ClassVar[int]
    dto_type: ClassVar[type]

    _dto_registry: DTORegistry = DTORegistry()

    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)

        cls._validate_dto_code()
        cls._validate_dto_type()

        cls._dto_registry.register(cls)

    def __init__(self, schema: type[T_DTO] | None = None) -> None:
        self._schema = schema

    @abstractmethod
    def serialize(self, value_dto: T_DTO) -> bytes:
        """Serialize DTO value to bytes for storage."""
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, raw_dto: bytes) -> T_DTO:
        """Deserialize bytes to original DTO value."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, value_dto: T_DTO, schema: type[T_DTO]) -> None:
        """Validate DTO value for given DTO schema."""
        raise NotImplementedError

    @classmethod
    def from_type(cls, dto_type: type[T_DTO]) -> type["BaseDTO"]:
        """Get DTO object from it type."""
        dto_object = cls._dto_registry.get_from_type(dto_type)
        if dto_object is None:
            raise DTOError(f"No DTO found for type: {dto_type}")
        return dto_object

    @classmethod
    def from_code(cls, dto_code: int) -> type["BaseDTO"]:
        """Get DTO object from it code."""
        dto_object = cls._dto_registry.get_from_code(dto_code)
        if dto_object is None:
            raise DTOError(f"No DTO found for code: {dto_code}")
        return dto_object

    @classmethod
    def _validate_dto_code(cls) -> None:
        if "dto_code" not in cls.__dict__:
            raise DTOError("Must define `dto_code`.")

        if not isinstance(cls.dto_code, int):
            raise DTOError("`dto_code` must be int type.")

        if cls.dto_code <= 0:
            raise DTOError("`dto_code` must be greater than zero.")

    @classmethod
    def _validate_dto_type(cls) -> None:
        if "dto_type" not in cls.__dict__:
            raise DTOError("Must define `dto_type`.")
