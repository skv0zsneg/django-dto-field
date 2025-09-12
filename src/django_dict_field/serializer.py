import bz2
import pickle
from typing import Any, ClassVar, Generic, Optional, TypeVar

P = TypeVar("P")


class Serializer(Generic[P]):
    """Params serializer & deserializer."""

    ALLOWED_TYPES: ClassVar[tuple[Any, ...]] = (dict,)

    def __init__(self, params_type: Optional[P] = None) -> None:
        self.params_type = params_type

    def serialize(self, value: P) -> bytes:
        serialized = pickle.dumps(value)
        compressed = bz2.compress(serialized)
        return compressed

    def deserialize(self, value: bytes) -> P:
        decompressed = bz2.decompress(value)
        deserialized = pickle.loads(decompressed)
        return deserialized

    def is_valid(self, value: P) -> bool:
        return any(
            map(
                lambda allowed_type: isinstance(value, allowed_type), self.ALLOWED_TYPES
            )
        )
