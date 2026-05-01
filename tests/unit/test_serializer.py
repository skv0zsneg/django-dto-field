import struct

import pytest

from django_dto_field.exceptions import CorruptedDtoError, DtoFeatureError, SerializerError
from django_dto_field.features.serializers import BaseDtoSerializer, DictDtoSerializer


@pytest.fixture
def serializer() -> DictDtoSerializer:
    return DictDtoSerializer()


class TestDictDtoSerializer:
    @pytest.mark.parametrize(
        "value",
        [
            {},
            {"key": "value"},
            {"nested": {"a": 1, "b": [1, 2, 3]}},
            {"null": None, "bool": True, "int": 42, "float": 3.14},
        ],
    )
    def test_serialize_and_deserialize_roundtrip(
        self, serializer: DictDtoSerializer, value: dict
    ) -> None:
        raw = serializer.serialize(value)
        assert isinstance(raw, bytes)
        assert raw[:1] == b"\x01"

        restored = serializer.deserialize(raw)
        assert restored == value

    def test_deserialize_handles_none(self, serializer: DictDtoSerializer) -> None:
        assert serializer.deserialize(None) is None

    def test_deserialize_wrong_dto_code_raises(self, serializer: DictDtoSerializer) -> None:
        payload = b'{"test": 1}'
        raw_wrong_code = b"\x02" + struct.pack("!I", len(payload)) + payload

        with pytest.raises(SerializerError, match=r"expected.*got"):
            serializer.deserialize(raw_wrong_code)

    def test_deserialize_truncated_payload_raises(self, serializer: DictDtoSerializer) -> None:
        payload = b'{"test": 1}'
        raw_truncated = b"\x01" + struct.pack("!I", len(payload)) + payload[:-2]

        with pytest.raises(CorruptedDtoError, match="payload truncated"):
            serializer.deserialize(raw_truncated)


class TestBaseDtoSerializerConstraints:
    def test_abstract_class_cannot_be_instantiated(self) -> None:
        with pytest.raises(
            DtoFeatureError, match="Dto Feature Error: missing definition of `dto_code`"
        ):
            BaseDtoSerializer()

    def test_missing_dto_code_raises_on_init(self) -> None:
        class BrokenSerializer(BaseDtoSerializer):
            dto_code = None

            def serialize_payload(self, v):  # pragma: no cover
                return b""

            def deserialize_payload(self, v):  # pragma: no cover
                return {}

        with pytest.raises(
            DtoFeatureError,
            match="Dto Feature Error: missing definition of `dto_code`.",
        ):
            BrokenSerializer()

    def test_serialize_payload_not_implemented(self) -> None:
        class IncompleteSerializer(BaseDtoSerializer):
            dto_code = b"\x99"
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteSerializer()
