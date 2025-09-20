import orjson


class Serializer:
    """Params serializer & deserializer."""

    def serialize(self, value: dict) -> bytes:
        return orjson.dumps(value)

    def deserialize(self, value: bytes) -> dict:
        return orjson.loads(value)
