import dataclasses
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from django_dto_field.exceptions import DtoHandlerError, ValidatorError
from django_dto_field.features.base import DtoCodeEnum
from django_dto_field.handler import DtoHandler


@dataclasses.dataclass
class _DummyDataclass:
    value: int


@pytest.fixture(scope="function")
def handler() -> DtoHandler[Any]:
    return DtoHandler()


class TestDtoHandlerSerialize:
    @patch("django_dto_field.handler.DictDtoSerializer")
    def test_serialize_delegates_to_dict_serializer(
        self, mock_cls: MagicMock, handler: DtoHandler
    ) -> None:
        dto = {"key": "value", "nested": [1, 2]}
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        mock_instance.serialize.return_value = b"\x01\x00\x00\x00\x00"

        result = handler.serialize(dto)

        mock_cls.assert_called_once()
        mock_instance.serialize.assert_called_once_with(dto)
        assert result == b"\x01\x00\x00\x00\x00"

    @patch("django_dto_field.handler.DataclassDtoSerializer")
    def test_serialize_delegates_to_dataclass_serializer(
        self, mock_cls: MagicMock, handler: DtoHandler
    ) -> None:
        dto = _DummyDataclass(value=42)
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        mock_instance.serialize.return_value = b"\x02\x00\x00\x00\x02"

        result = handler.serialize(dto)

        mock_cls.assert_called_once()
        mock_instance.serialize.assert_called_once_with(dto)
        assert result == b"\x02\x00\x00\x00\x02"

    @pytest.mark.parametrize(
        "unsupported_value",
        [
            pytest.param(42, id="int"),
            pytest.param("string", id="str"),
            pytest.param([1, 2, 3], id="list"),
            pytest.param(None, id="none"),
            pytest.param(object(), id="generic_object"),
        ],
    )
    def test_serialize_raises_on_unsupported_type(
        self, handler: DtoHandler, unsupported_value: Any
    ) -> None:
        with pytest.raises(DtoHandlerError):
            handler.serialize(unsupported_value)


class TestDtoHandlerDeserialize:
    @patch("django_dto_field.handler.RawDtoParser.get_serializer_code")
    @patch("django_dto_field.handler.DictDtoSerializer")
    def test_deserialize_dict_with_schema_none(
        self,
        mock_dict_cls: MagicMock,
        mock_parser: MagicMock,
        handler: DtoHandler,
    ) -> None:
        mock_parser.return_value = DtoCodeEnum.DICT
        mock_instance = MagicMock()
        mock_dict_cls.return_value = mock_instance
        mock_instance.deserialize.return_value = {"restored": True}
        raw_dto = b"\x01\x00\x00\x00\x04data"

        result = handler.deserialize(raw_dto)

        mock_parser.assert_called_once_with(raw_dto)
        mock_dict_cls.assert_called_once_with(None)
        mock_instance.deserialize.assert_called_once_with(raw_dto)
        assert result == {"restored": True}

    @patch("django_dto_field.handler.RawDtoParser.get_serializer_code")
    @patch("django_dto_field.handler.DataclassDtoSerializer")
    def test_deserialize_dataclass_with_explicit_schema(
        self,
        mock_dc_cls: MagicMock,
        mock_parser: MagicMock,
        handler: DtoHandler,
    ) -> None:
        mock_parser.return_value = DtoCodeEnum.DATACLASS
        mock_instance = MagicMock()
        mock_dc_cls.return_value = mock_instance
        mock_instance.deserialize.return_value = _DummyDataclass(value=99)
        raw_dto = b"\x02\x00\x00\x00\x02dc"

        result = handler.deserialize(raw_dto, schema=_DummyDataclass)

        mock_parser.assert_called_once_with(raw_dto)
        mock_dc_cls.assert_called_once_with(_DummyDataclass)
        mock_instance.deserialize.assert_called_once_with(raw_dto)
        assert isinstance(result, _DummyDataclass)
        assert result.value == 99

    @patch("django_dto_field.handler.RawDtoParser.get_serializer_code")
    def test_deserialize_raises_on_unknown_code(
        self, mock_parser: MagicMock, handler: DtoHandler
    ) -> None:
        mock_parser.return_value = b"\xff"  # Код, отсутствующий в маппинге
        with pytest.raises(DtoHandlerError, match="no serializer for DTO value"):
            handler.deserialize(b"\xff\x00\x00\x00\x00truncated")


class TestDtoHandlerIsValid:
    @patch("django_dto_field.handler.DataclassValidator")
    def test_is_valid_returns_true_on_success(
        self, mock_validator_cls: MagicMock, handler: DtoHandler
    ) -> None:
        mock_validator = MagicMock()
        mock_validator_cls.return_value = mock_validator
        dto = _DummyDataclass(value=10)

        assert handler.is_valid(dto, _DummyDataclass) is True
        mock_validator_cls.assert_called_once()
        mock_validator.validate.assert_called_once_with(dto, _DummyDataclass)

    @patch("django_dto_field.handler.DataclassValidator")
    def test_is_valid_returns_false_on_validator_error(
        self, mock_validator_cls: MagicMock, handler: DtoHandler
    ) -> None:
        mock_validator = MagicMock()
        mock_validator_cls.return_value = mock_validator
        mock_validator.validate.side_effect = ValidatorError("invalid payload")
        dto = _DummyDataclass(value=-5)

        assert handler.is_valid(dto, _DummyDataclass) is False
        mock_validator.validate.assert_called_once()

    @patch("django_dto_field.handler.DataclassValidator")
    def test_is_valid_raises_when_schema_is_instance(
        self, mock_validator_cls: MagicMock, handler: DtoHandler
    ) -> None:
        """Ветка: `inspect.isclass(schema)` возвращает False для экземпляра dataclass."""
        dto_instance = _DummyDataclass(value=1)
        schema_instance = _DummyDataclass(value=1)

        with pytest.raises(
            DtoHandlerError, match="dataclass schema must be class but instance is given"
        ):
            handler.is_valid(dto_instance, schema_instance)

        mock_validator_cls.assert_not_called()

    @pytest.mark.parametrize(
        "unsupported_schema",
        [
            pytest.param(dict, id="dict_type"),
            pytest.param(list, id="list_type"),
            pytest.param("NotAType", id="str_instead_of_type"),
        ],
    )
    def test_is_valid_raises_on_unsupported_schema(
        self, handler: DtoHandler, unsupported_schema: type[Any]
    ) -> None:
        with pytest.raises(DtoHandlerError, match="no validator for schema"):
            handler.is_valid({"dummy": 1}, unsupported_schema)
