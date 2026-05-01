from dataclasses import dataclass, field
from typing import Any

import pytest

from django_dto_field.exceptions import ValidatorError
from django_dto_field.features.validators import DataclassValidator


@pytest.fixture
def validator() -> DataclassValidator:
    return DataclassValidator()


@dataclass
class SimpleDTO:
    value: int


@dataclass
class AnotherDTO:
    name: str


@dataclass
class ChildDTO(SimpleDTO):
    extra: str


@dataclass(frozen=True)
class FrozenDTO:
    token: str


@dataclass
class DTOWithDefaults:
    req: int
    opt: str = "default"
    computed: float = field(init=False, default=0.0)


@pytest.mark.parametrize(
    "value, schema",
    [
        pytest.param(SimpleDTO(value=42), SimpleDTO, id="exact_match"),
        pytest.param(AnotherDTO(name="test"), AnotherDTO, id="different_schema"),
        pytest.param(ChildDTO(value=1, extra="x"), ChildDTO, id="child_matches_child"),
        pytest.param(ChildDTO(value=1, extra="x"), SimpleDTO, id="child_matches_parent_isinstance"),
        pytest.param(FrozenDTO(token="abc"), FrozenDTO, id="frozen_dataclass"),
        pytest.param(DTOWithDefaults(req=1), DTOWithDefaults, id="defaults_and_init_false"),
    ],
)
def test_valid_instance(validator: DataclassValidator, value: Any, schema: type) -> None:
    # Не должно вызывать исключений
    validator.validate(value, schema)


@pytest.mark.parametrize(
    "value, schema",
    [
        pytest.param(SimpleDTO(value=42), AnotherDTO, id="instance_wrong_schema"),
        pytest.param({"value": 42}, SimpleDTO, id="dict_instead_of_instance"),
        pytest.param([1, 2, 3], SimpleDTO, id="list_instead_of_instance"),
        pytest.param("string", SimpleDTO, id="str_instead_of_instance"),
        pytest.param(42, SimpleDTO, id="int_instead_of_instance"),
        pytest.param(None, SimpleDTO, id="none_input"),
        pytest.param(object(), SimpleDTO, id="bare_object"),
    ],
)
def test_invalid_input(validator: DataclassValidator, value: Any, schema: type) -> None:
    with pytest.raises(ValidatorError):
        validator.validate(value, schema)


def test_error_message_contains_schema_name(validator: DataclassValidator) -> None:
    with pytest.raises(ValidatorError) as exc_info:
        validator.validate({"foo": "bar"}, SimpleDTO)

    assert "SimpleDTO" in str(exc_info.value)
    assert "not match given schema" in str(exc_info.value)
