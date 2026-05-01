import dataclasses
from typing import Any

import pytest

from django_dto_field.exceptions import DtoFeatureError, ValidatorError
from django_dto_field.features.base import DtoCodeEnum
from django_dto_field.features.validators import BaseDtoValidator, DataclassValidator


@dataclasses.dataclass
class _BaseDTO:
    id: int


@dataclasses.dataclass
class _DerivedDTO(_BaseDTO):
    name: str


@dataclasses.dataclass(frozen=True)
class _FrozenDTO:
    token: str


@pytest.fixture(scope="function")
def validator() -> DataclassValidator:
    return DataclassValidator()


class TestBaseDtoValidator:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseDtoValidator()

    def test_abstract_method_enforcement(self) -> None:
        """Subclass without `validate` implementation must fail at instantiation."""

        class IncompleteValidator(BaseDtoValidator):
            dto_code = b"\x99"

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteValidator()

    def test_missing_dto_code_raises_dto_feature_error(self) -> None:
        """Inherited guard from BaseDtoFeature must trigger on init."""

        class BrokenValidator(BaseDtoValidator):
            def validate(self, value_dto: Any, schema: type) -> None:
                pass

        with pytest.raises(DtoFeatureError, match="missing definition of `dto_code`"):
            BrokenValidator()


class TestDataclassValidator:
    def test_dto_code_is_correctly_assigned(self) -> None:
        assert DataclassValidator.dto_code == DtoCodeEnum.DATACLASS
        assert isinstance(DataclassValidator.dto_code, bytes)

    @pytest.mark.parametrize(
        "value, schema",
        [
            pytest.param(_BaseDTO(id=1), _BaseDTO, id="exact_type_match"),
            pytest.param(_DerivedDTO(id=2, name="test"), _DerivedDTO, id="derived_exact_match"),
            pytest.param(_DerivedDTO(id=3, name="test"), _BaseDTO, id="derived_isinstance_base"),
            pytest.param(_FrozenDTO(token="xyz"), _FrozenDTO, id="frozen_dataclass"),
            pytest.param(_BaseDTO(id=0), _BaseDTO, id="zero_value_instance"),
        ],
    )
    def test_validate_returns_none_on_success(
        self, validator: DataclassValidator, value: Any, schema: type
    ) -> None:
        result = validator.validate(value, schema)
        assert result is None

    @pytest.mark.parametrize(
        "value, schema",
        [
            pytest.param(_BaseDTO(id=1), _FrozenDTO, id="wrong_dataclass_type"),
            pytest.param({"id": 1}, _BaseDTO, id="dict_instead_of_instance"),
            pytest.param([1, 2], _BaseDTO, id="list_instead_of_instance"),
            pytest.param("string_payload", _BaseDTO, id="str_instead_of_instance"),
            pytest.param(42, _BaseDTO, id="int_instead_of_instance"),
            pytest.param(None, _BaseDTO, id="none_value"),
            pytest.param(object(), _BaseDTO, id="bare_object_instance"),
        ],
    )
    def test_validate_raises_on_type_mismatch(
        self, validator: DataclassValidator, value: Any, schema: type
    ) -> None:
        with pytest.raises(ValidatorError, match="given dataclass DTO is not match given schema"):
            validator.validate(value, schema)

    def test_error_message_includes_schema_name(self, validator: DataclassValidator) -> None:
        with pytest.raises(ValidatorError) as exc_info:
            validator.validate(_BaseDTO(id=1), _DerivedDTO)

        error_msg = str(exc_info.value)
        assert "Validation Error:" in error_msg
        assert "_DerivedDTO" in error_msg
        assert "not match given schema" in error_msg

    def test_validate_with_invalid_schema_type_raises_type_error(self) -> None:
        """
        isinstance() бросает TypeError, если schema не является классом/типом.
        Текущий контракт не перехватывает это исключение, поэтому тестируем проброс.
        """
        validator = DataclassValidator()
        with pytest.raises(TypeError, match="isinstance\\(\\) arg 2 must be a type"):
            validator.validate(_BaseDTO(id=1), "not_a_type")  # type: ignore[arg-type]
