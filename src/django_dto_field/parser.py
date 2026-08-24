import struct
from typing import Final

from django_dto_field.exceptions import BinaryDTOParserError


class BinaryDTOParser:
    """Parser DTO to binary representation.

    Pack and unpack in custom binary format. It contains 3 parts in next order:
    1. DTO code (1 byte). This is code defining DTO type.
    2. Payload length (4 bytes). Length of the serialized payload.
    3. Payload (variable length). The actual serialized data.
    """

    _header_size: Final[int] = 5
    _length_format: Final[str] = "!I"
    _max_dto_code: Final[int] = 255

    def pack(self, dto_code: int, payload: bytes) -> bytes:
        """Pack raw DTO into binary format."""
        if not isinstance(dto_code, int) or not 0 <= dto_code <= self._max_dto_code:
            raise BinaryDTOParserError("DTO code unexpected not 1 byte size.")
        byte_dto_code = bytes([dto_code])

        return byte_dto_code + struct.pack(self._length_format, len(payload)) + payload

    def unpack(self, raw_dto: bytes) -> tuple[int, bytes]:
        """Unpack binary into DTO code and payload."""
        if len(raw_dto) < self._header_size:
            raise BinaryDTOParserError("Corrupted: Header DTO to short.")

        binary_payload_length = raw_dto[1 : self._header_size]
        try:
            payload_length = struct.unpack(self._length_format, binary_payload_length)[
                0
            ]
        except Exception as error_on_unpacking:
            raise BinaryDTOParserError(
                "Corrupted: cannot unpack payload length number."
            ) from error_on_unpacking

        payload = raw_dto[self._header_size : self._header_size + payload_length]
        if len(payload) != payload_length:
            raise BinaryDTOParserError("Corrupted: payload truncated")

        return int(raw_dto[0]), payload
