import msgspec


class Serializer:
    """Params serializer & deserializer."""

    def serialize(self, value: dict) -> bytes:
        return msgspec.json.encode(value)

    def deserialize(self, value: bytes) -> dict:
        return msgspec.json.decode(value)
