from unittest.mock import MagicMock, patch

import pytest

from django_dto_field.dto.exceptions import DTOSerializeError, DTOValidationError
from django_dto_field.handler import HandlerDTO


@pytest.fixture
def handler() -> HandlerDTO:
    return HandlerDTO()


@patch("django_dto_field.handler.BinaryDTOParser")
@patch("django_dto_field.handler.BaseDTO")
def test_serialize(
    mock_base_dto: MagicMock, mock_parser_cls: MagicMock, handler: HandlerDTO
) -> None:
    dto_instance = MagicMock(dto_code=42)
    dto_instance.serialize.return_value = b"payload"
    mock_base_dto.from_type.return_value.return_value = dto_instance

    parser_instance = MagicMock()
    parser_instance.pack.return_value = b"packed"
    mock_parser_cls.return_value = parser_instance

    value = MagicMock()
    result = handler.serialize(value)

    mock_base_dto.from_type.assert_called_once_with(type(value))
    dto_instance.serialize.assert_called_once_with(value)
    parser_instance.pack.assert_called_once_with(42, b"payload")
    assert result == b"packed"


@patch("django_dto_field.handler.BinaryDTOParser")
@patch("django_dto_field.handler.BaseDTO")
def test_deserialize_with_schema(
    mock_base_dto: MagicMock, mock_parser_cls: MagicMock, handler: HandlerDTO
) -> None:
    dto_instance = MagicMock(dto_code=7)
    dto_instance.deserialize.return_value = "dto_obj"
    mock_base_dto.from_type.return_value.return_value = dto_instance

    parser_instance = MagicMock()
    parser_instance.unpack.return_value = (7, b"data")
    mock_parser_cls.return_value = parser_instance

    schema = MagicMock()
    result = handler.deserialize(b"raw", schema)

    mock_base_dto.from_type.assert_called_once_with(schema)
    mock_base_dto.from_code.assert_not_called()
    assert result == "dto_obj"


@patch("django_dto_field.handler.BinaryDTOParser")
@patch("django_dto_field.handler.BaseDTO")
def test_deserialize_without_schema(
    mock_base_dto: MagicMock, mock_parser_cls: MagicMock, handler: HandlerDTO
) -> None:
    dto_instance = MagicMock(dto_code=3)
    dto_instance.deserialize.return_value = "dto_obj"
    mock_base_dto.from_code.return_value.return_value = dto_instance

    parser_instance = MagicMock()
    parser_instance.unpack.return_value = (3, b"data")
    mock_parser_cls.return_value = parser_instance

    result = handler.deserialize(b"raw", None)

    mock_base_dto.from_code.assert_called_once_with(3)
    mock_base_dto.from_type.assert_not_called()
    assert result == "dto_obj"


@patch("django_dto_field.handler.BinaryDTOParser")
@patch("django_dto_field.handler.BaseDTO")
def test_deserialize_code_mismatch(
    mock_base_dto: MagicMock, mock_parser_cls: MagicMock, handler: HandlerDTO
) -> None:
    dto_instance = MagicMock(dto_code=99)
    mock_base_dto.from_type.return_value.return_value = dto_instance

    parser_instance = MagicMock()
    parser_instance.unpack.return_value = (1, b"data")
    mock_parser_cls.return_value = parser_instance

    with pytest.raises(DTOSerializeError, match="DTO code mismatch"):
        handler.deserialize(b"raw", MagicMock())


@patch("django_dto_field.handler.BaseDTO")
def test_is_valid_true(mock_base_dto: MagicMock, handler: HandlerDTO) -> None:
    dto_instance = MagicMock()
    mock_base_dto.from_type.return_value.return_value = dto_instance

    schema = MagicMock()
    value = MagicMock()
    assert handler.is_valid(value, schema) is True
    dto_instance.validate.assert_called_once_with(value, schema)


@patch("django_dto_field.handler.BaseDTO")
def test_is_valid_false(mock_base_dto: MagicMock, handler: HandlerDTO) -> None:
    dto_instance = MagicMock()
    dto_instance.validate.side_effect = DTOValidationError("bad")
    mock_base_dto.from_type.return_value.return_value = dto_instance

    assert handler.is_valid(MagicMock(), MagicMock()) is False
