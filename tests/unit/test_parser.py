import struct
from unittest.mock import patch

import pytest

from django_dto_field.exceptions import CorruptedDtoError
from django_dto_field.parser import RawDtoParser


@pytest.fixture(scope="function")
def parser() -> RawDtoParser:
    return RawDtoParser()


class TestRawDtoParserToRaw:
    @pytest.mark.parametrize(
        "payload, expected_length_bytes",
        [
            pytest.param(b"", struct.pack("!I", 0), id="empty_payload"),
            pytest.param(b"\x00", struct.pack("!I", 1), id="single_null_byte"),
            pytest.param(b"hello world", struct.pack("!I", 11), id="ascii_string"),
            pytest.param(b"\x00\xff\x7f", struct.pack("!I", 3), id="binary_data"),
            pytest.param(bytes(range(256)), struct.pack("!I", 256), id="full_byte_range"),
            pytest.param(b"x" * 10_000, struct.pack("!I", 10_000), id="large_payload"),
        ],
    )
    def test_to_raw_valid_roundtrip(
        self,
        parser: RawDtoParser,
        payload: bytes,
        expected_length_bytes: bytes,
    ) -> None:
        code = b"\x01"
        raw = parser.to_raw(code, payload)

        assert raw[:1] == code
        assert raw[1:5] == expected_length_bytes
        assert raw[5:] == payload
        assert len(raw) == 1 + 4 + len(payload)

    @pytest.mark.parametrize(
        "invalid_code",
        [
            pytest.param(b"", id="empty_code"),
            pytest.param(b"ab", id="two_bytes_code"),
            pytest.param(b"\x00" * 10, id="long_code"),
        ],
    )
    def test_to_raw_invalid_code_length(self, parser: RawDtoParser, invalid_code: bytes) -> None:
        with pytest.raises(CorruptedDtoError, match="serializer code unexpected not 1 byte size"):
            parser.to_raw(invalid_code, b"data")


class TestRawDtoParserFromRaw:
    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param(b"", id="empty_payload"),
            pytest.param(b"0", id="single_byte"),
            pytest.param(b"test \x00\xff data", id="mixed_binary"),
            pytest.param(b"a" * 1_000, id="large_payload"),
        ],
    )
    def test_from_raw_valid_roundtrip(self, parser: RawDtoParser, payload: bytes) -> None:
        code = b"\x02"
        raw = parser.to_raw(code, payload)
        assert parser.from_raw(raw) == payload

    def test_from_raw_zero_length_payload_boundary(self, parser: RawDtoParser) -> None:
        raw = b"\x03" + struct.pack("!I", 0)
        assert parser.from_raw(raw) == b""
        assert len(raw) == RawDtoParser._header_size

    @pytest.mark.parametrize(
        "short_data",
        [
            pytest.param(b"", id="0_bytes"),
            pytest.param(b"\x01", id="1_byte"),
            pytest.param(b"\x01\x00", id="2_bytes"),
            pytest.param(b"\x01\x00\x00", id="3_bytes"),
            pytest.param(b"\x01\x00\x00\x00", id="4_bytes"),
        ],
    )
    def test_from_raw_header_too_short(self, parser: RawDtoParser, short_data: bytes) -> None:
        with pytest.raises(CorruptedDtoError, match="Header DTO to short"):
            parser.from_raw(short_data)

    def test_from_raw_truncated_payload(self, parser: RawDtoParser) -> None:
        declared_len = 100
        actual_payload = b"short"
        raw = b"\x03" + struct.pack("!I", declared_len) + actual_payload

        with pytest.raises(CorruptedDtoError, match="payload truncated"):
            parser.from_raw(raw)

    @patch("django_dto_field.parser.struct.unpack")
    def test_from_raw_unpack_error_with_exception_chaining(
        self, mock_unpack, parser: RawDtoParser
    ) -> None:
        mock_unpack.side_effect = struct.error("mocked unpack failure")
        raw = b"\x01" + struct.pack("!I", 10) + b"data"

        with pytest.raises(
            CorruptedDtoError, match="cannot unpack payload length number"
        ) as exc_info:
            parser.from_raw(raw)

        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, struct.error)
        assert str(exc_info.value.__cause__) == "mocked unpack failure"


class TestRawDtoParserGetSerializerCode:
    @pytest.mark.parametrize(
        "raw_dto, expected_code",
        [
            pytest.param(b"\xa5" + struct.pack("!I", 3) + b"xyz", b"\xa5", id="standard_dto"),
            pytest.param(b"\x00" + struct.pack("!I", 0), b"\x00", id="zero_code_zero_payload"),
            pytest.param(b"\xff" * 10, b"\xff", id="arbitrary_long_data"),
        ],
    )
    def test_get_serializer_code_valid(
        self, parser: RawDtoParser, raw_dto: bytes, expected_code: bytes
    ) -> None:
        assert parser.get_serializer_code(raw_dto) == expected_code
        assert RawDtoParser.get_serializer_code(raw_dto) == expected_code

    @pytest.mark.parametrize(
        "short_data",
        [
            pytest.param(b"", id="0_bytes"),
            pytest.param(b"\x01\x00\x00\x00", id="4_bytes"),
        ],
    )
    def test_get_serializer_code_header_too_short(
        self, parser: RawDtoParser, short_data: bytes
    ) -> None:
        with pytest.raises(CorruptedDtoError, match="Header DTO too short"):
            parser.get_serializer_code(short_data)
