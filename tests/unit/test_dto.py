from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from django_dto_field.dto.base import BaseDTO, DTORegistry
from django_dto_field.dto.dataclasses import DataclassDTO
from django_dto_field.dto.dict import DictDTO
from django_dto_field.dto.exceptions import DTOError, DTOValidationError
from django_dto_field.exceptions import (
    BaseDjangoDTOFieldError,
    BinaryDTOParserError,
    DtoFeatureError,
    DtoHandlerError,
    RegistryError,
    SerializerError,
    ValidatorError,
)
from django_dto_field.handler import HandlerDTO
from django_dto_field.parser import BinaryDTOParser


@dataclass
class Person:
    name: str
    age: int


@dataclass
class OtherPerson:
    name: str


def test_dict_dto_round_trip_and_validation() -> None:
    dto = DictDTO()
    value = {"nested": [1, None, True]}
    assert dto.deserialize(dto.serialize(value)) == value
    assert dto.validate(value, dict) is None


def test_dataclass_dto_round_trip_validation_and_schema_errors() -> None:
    dto = DataclassDTO(Person)
    value = Person("Ada", 37)
    assert dto.deserialize(dto.serialize(value)) == value
    assert dto.validate(value, Person) is None

    with pytest.raises(DTOValidationError, match="not match"):
        dto.validate(value, OtherPerson)
    with pytest.raises(DTOValidationError, match="must be provided"):
        DataclassDTO().deserialize(b"{}")
    with pytest.raises(DTOValidationError, match="Expected dataclass"):
        DataclassDTO(object()).deserialize(b"{}")  # type: ignore[arg-type]


def test_registry_lookup_duplicate_checks_and_base_dto_errors() -> None:
    registry = DTORegistry()

    class FirstDTO:
        dto_code = 10
        dto_type = str

    class DuplicateCode:
        dto_code = 10
        dto_type = bytes

    class DuplicateType:
        dto_code = 11
        dto_type = str

    registry.register(FirstDTO)  # type: ignore[arg-type]
    assert registry.get_from_code(10) is FirstDTO
    assert registry.get_from_type(str) is FirstDTO
    assert registry.get_from_code(999) is None
    assert registry.get_from_type(int) is None
    assert BaseDTO.from_type(dict) is DictDTO
    with pytest.raises(DTOError, match="already reserved"):
        registry.register(DuplicateCode)  # type: ignore[arg-type]
    with pytest.raises(DTOError, match="already reserved"):
        registry.register(DuplicateType)  # type: ignore[arg-type]
    with pytest.raises(DTOError, match="No DTO found for type"):
        BaseDTO.from_type(tuple)
    with pytest.raises(DTOError, match="No DTO found for code"):
        BaseDTO.from_code(250)


def test_handler_supports_dict_schema_and_generic_dto_code_lookup() -> None:
    handler = HandlerDTO()
    value = {"key": "value"}
    assert handler.deserialize(handler.serialize(value), dict) == value
    assert handler.is_valid(value, dict) is True


@pytest.mark.parametrize(
    ("attrs", "message"),
    [
        ({"dto_type": int}, "Must define `dto_code`"),
        ({"dto_code": "x", "dto_type": int}, "must be int"),
        ({"dto_code": 0, "dto_type": int}, "greater than zero"),
        ({"dto_code": 41}, "Must define `dto_type`"),
    ],
)
def test_base_dto_subclass_definition_requires_valid_metadata(attrs: dict, message: str) -> None:
    with pytest.raises(DTOError, match=message):
        type("InvalidDTO", (BaseDTO,), attrs)


def test_base_dto_abstract_method_default_bodies() -> None:
    class ConcreteDTO(BaseDTO):
        dto_code = 42
        dto_type = tuple

        def serialize(self, value: tuple) -> bytes:
            return super().serialize(value)

        def deserialize(self, raw: bytes) -> tuple:
            return super().deserialize(raw)

        def validate(self, value: tuple, schema: type) -> None:
            super().validate(value, schema)

    dto = ConcreteDTO()
    with pytest.raises(NotImplementedError):
        dto.serialize(())
    with pytest.raises(NotImplementedError):
        dto.deserialize(b"")
    with pytest.raises(NotImplementedError):
        dto.validate((), tuple)


@pytest.mark.parametrize("invalid_code", [-1, 256, "one"])
def test_parser_rejects_non_single_byte_codes(invalid_code: object) -> None:
    with pytest.raises(BinaryDTOParserError, match="not 1 byte"):
        BinaryDTOParser().pack(invalid_code, b"data")  # type: ignore[arg-type]


def test_parser_round_trip_and_corruption_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    parser = BinaryDTOParser()
    raw = parser.pack(2, b"payload")
    assert parser.unpack(raw) == (2, b"payload")
    with pytest.raises(BinaryDTOParserError, match="Header DTO"):
        parser.unpack(b"\x01")
    with pytest.raises(BinaryDTOParserError, match="payload truncated"):
        parser.unpack(b"\x01\x00\x00\x00\x02x")

    def broken_unpack(*args: object) -> object:
        raise ValueError("broken")

    monkeypatch.setattr("django_dto_field.parser.struct.unpack", broken_unpack)
    with pytest.raises(BinaryDTOParserError, match="cannot unpack") as error:
        parser.unpack(b"\x01\x00\x00\x00\x00")
    assert isinstance(error.value.__cause__, ValueError)


@pytest.mark.parametrize(
    "exception_type",
    [
        BaseDjangoDTOFieldError,
        DtoHandlerError,
        SerializerError,
        BinaryDTOParserError,
        RegistryError,
        DtoFeatureError,
        ValidatorError,
        DTOError,
        DTOValidationError,
    ],
)
def test_exceptions_support_default_and_explicit_messages(exception_type: type[Exception]) -> None:
    assert str(exception_type())
    assert str(exception_type("custom")) == "custom"
