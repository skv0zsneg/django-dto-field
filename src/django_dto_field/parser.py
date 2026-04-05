import struct
from typing import Final

from django_dto_field.exceptions import CorruptedDtoError


class RawDtoParser:
    """Parser for raw DTO representation."""

    _header_size: Final[int] = 5
    _length_format: Final[str] = "!I"

    def to_raw(self, serializer_code: bytes, payload: bytes) -> bytes:
        if len(serializer_code) != 1:
            raise CorruptedDtoError("Corrupted: serializer code unexpected not 1 byte size.")

        length_payload = struct.pack(self._length_format, len(payload))
        if len(length_payload) != 4:
            raise CorruptedDtoError("Corrupted: length payload unexpected not 4 byte size.")

        return serializer_code + length_payload + payload

    def from_raw(self, raw_dto: bytes) -> bytes:
        if len(raw_dto) < self._header_size:
            raise CorruptedDtoError("Corrupted: Header DTO to short.")

        try:
            payload_length = struct.unpack(
                self._length_format,
                raw_dto[1 : self._header_size],
            )[0]
        except Exception as e:
            raise CorruptedDtoError("Corrupted: cannot unpack payload length number.") from e

        payload = raw_dto[self._header_size : self._header_size + payload_length]
        if len(payload) != payload_length:
            raise CorruptedDtoError("Corrupted: payload truncated")

        return payload

    @classmethod
    def get_serializer_code(cls, raw_dto: bytes) -> bytes:
        if len(raw_dto) < cls._header_size:
            raise CorruptedDtoError("Corrupted: Header DTO to short.")
        return raw_dto[0:1]
