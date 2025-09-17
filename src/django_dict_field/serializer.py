import msgpack


class Serializer:
    """Params serializer & deserializer."""

    def serialize(self, value: dict) -> bytes:
        return msgpack.packb(value)

    def deserialize(self, value: bytes) -> dict:
        return msgpack.unpackb(value)
