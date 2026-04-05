import struct
from unittest.mock import patch

import pytest

from django_dto_field.exceptions import CorruptedDtoError
from django_dto_field.parser import RawDtoParser


@pytest.fixture
def parser() -> RawDtoParser:
    return RawDtoParser()


class TestToRaw:
    @pytest.mark.parametrize(
        "payload",
        [
            b"",
            b"hello world",
            b"\x00\xff\x7f",
            bytes(range(256)),
            b"x" * 10_000,
        ],
    )
    def test_to_raw_valid_roundtrip(self, parser: RawDtoParser, payload: bytes) -> None:
        code = b"\x01"
        raw = parser.to_raw(code, payload)

        assert raw[:1] == code
        expected_length = struct.pack("!I", len(payload))
        assert raw[1:5] == expected_length
        assert raw[5:] == payload

    @pytest.mark.parametrize("invalid_code", [b"", b"ab", b"\x00" * 10])
    def test_to_raw_invalid_code_length(self, parser: RawDtoParser, invalid_code: bytes) -> None:
        with pytest.raises(CorruptedDtoError, match="serializer code unexpected not 1 byte size"):
            parser.to_raw(invalid_code, b"data")


class TestFromRaw:
    def test_from_raw_valid(self, parser: RawDtoParser) -> None:
        payload = b"test \x00\xff data"
        raw = parser.to_raw(b"\x02", payload)
        assert parser.from_raw(raw) == payload

    def test_from_raw_header_too_short(self, parser: RawDtoParser) -> None:
        with pytest.raises(CorruptedDtoError, match="Header DTO to short"):
            parser.from_raw(b"\x01\x00\x00\x00")

    @patch("struct.unpack")
    def test_from_raw_unpack_raises(self, mock_unpack: patch, parser: RawDtoParser) -> None:
        """Ветка недостижима для валидных 4 байт, но покрывает except."""
        mock_unpack.side_effect = struct.error("mocked struct error")
        raw = b"\x01" + struct.pack("!I", 10) + b"data"
        with pytest.raises(CorruptedDtoError, match="cannot unpack payload length number"):
            parser.from_raw(raw)

    def test_from_raw_truncated_payload(self, parser: RawDtoParser) -> None:
        raw = b"\x03" + struct.pack("!I", 100) + b"short_payload"
        with pytest.raises(CorruptedDtoError, match="payload truncated"):
            parser.from_raw(raw)


class TestGetSerializerCode:
    def test_get_serializer_code_valid(self, parser: RawDtoParser) -> None:
        raw = b"\xa5" + struct.pack("!I", 3) + b"xyz"
        assert parser.get_serializer_code(raw) == b"\xa5"

    def test_get_serializer_code_header_too_short(self, parser: RawDtoParser) -> None:
        with pytest.raises(CorruptedDtoError, match="Header DTO too short"):
            parser.get_serializer_code(b"\x01\x00\x00\x00")
