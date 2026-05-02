import dataclasses
import struct
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from django_dto_field.exceptions import CorruptedDtoError, DtoFeatureError, SerializerError
from django_dto_field.features.base import DtoCodeEnum
from django_dto_field.features.serializers import (
    BaseDtoSerializer,
    DataclassDtoSerializer,
    DictDtoSerializer,
)


@dataclasses.dataclass
class _SampleDataclass:
    id: int
    name: str
    tags: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class _EmptyDataclass:
    pass


@pytest.fixture(scope="function")
def dict_serializer() -> DictDtoSerializer:
    return DictDtoSerializer()


@pytest.fixture(scope="function")
def dataclass_serializer() -> DataclassDtoSerializer:
    return DataclassDtoSerializer(schema=_SampleDataclass)


class TestBaseDtoSerializer:
    def test_init_initializes_parser_and_schema(self) -> None:
        class ConcreteSerializer(BaseDtoSerializer[dict]):
            dto_code = b"\x99"

            def serialize_payload(self, v: dict) -> bytes:
                return b""

            def deserialize_payload(self, v: bytes) -> dict:
                return {}

        serializer = ConcreteSerializer(schema=dict)
        assert serializer._schema is dict
        # RawDtoParser инстанцируется без аргументов
        assert hasattr(serializer, "_parser")

    def test_missing_dto_code_raises_on_init(self) -> None:
        class BrokenSerializer(BaseDtoSerializer):
            dto_code = None

            def serialize_payload(self, v: Any) -> bytes:
                return b""

            def deserialize_payload(self, v: bytes) -> Any:
                return None

        with pytest.raises(DtoFeatureError, match="missing definition of `dto_code`"):
            BrokenSerializer()

    def test_unimplemented_abstract_methods_raise(self) -> None:
        class IncompleteSerializer(BaseDtoSerializer):
            dto_code = b"\x99"

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteSerializer()

    @patch("django_dto_field.features.serializers.RawDtoParser.to_raw")
    def test_serialize_delegates_to_parser(
        self, mock_to_raw: MagicMock, dict_serializer: DictDtoSerializer
    ) -> None:
        mock_to_raw.return_value = b"\x01\x00\x00\x00\x00"
        payload = {"key": "value"}

        result = dict_serializer.serialize(payload)

        mock_to_raw.assert_called_once_with(DtoCodeEnum.DICT, mock_to_raw.call_args[0][1])
        assert result == b"\x01\x00\x00\x00\x00"

    def test_deserialize_returns_none_on_none_input(
        self, dict_serializer: DictDtoSerializer
    ) -> None:
        assert dict_serializer.deserialize(None) is None

    @patch("django_dto_field.features.serializers.RawDtoParser.get_serializer_code")
    def test_deserialize_raises_on_code_mismatch(
        self, mock_get_code: MagicMock, dict_serializer: DictDtoSerializer
    ) -> None:
        mock_get_code.return_value = DtoCodeEnum.DATACLASS
        with pytest.raises(SerializerError, match=r"Serialize Code Error: expected.*got"):
            dict_serializer.deserialize(b"\x02" + b"\x00" * 4 + b"{}")


class TestDictDtoSerializer:
    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param({}, id="empty_dict"),
            pytest.param({"key": "value", "num": 42}, id="flat_dict"),
            pytest.param({"nested": {"a": [1, None, True]}}, id="nested_complex"),
            pytest.param({"null": None, "bool": False, "float": 3.14159}, id="json_primitives"),
            pytest.param({f"{i}": f"{i+1}" for i in range(10_000)}, id="large_dict"),
        ],
    )
    def test_serialize_deserialize_roundtrip(
        self, dict_serializer: DictDtoSerializer, payload: dict[str, Any]
    ) -> None:
        raw = dict_serializer.serialize(payload)
        assert raw[:1] == DtoCodeEnum.DICT
        restored = dict_serializer.deserialize(raw)
        assert restored == payload

    def test_deserialize_truncated_payload_raises(self, dict_serializer: DictDtoSerializer) -> None:
        truncated_raw = b"\x01" + struct.pack("!I", 10) + b"ab"
        with pytest.raises(CorruptedDtoError, match="Corrupted: payload truncated"):
            dict_serializer.deserialize(truncated_raw)

    def test_deserialize_handles_none(self, dict_serializer: DictDtoSerializer) -> None:
        assert dict_serializer.deserialize(None) is None


class TestDataclassDtoSerializer:
    @pytest.mark.parametrize(
        "instance",
        [
            pytest.param(
                _SampleDataclass(id=1, name="alice", tags=["dev", "py"]), id="populated_dc"
            ),
            pytest.param(_SampleDataclass(id=0, name="bob"), id="default_factory"),
            pytest.param(_EmptyDataclass(), id="empty_dc"),
        ],
    )
    def test_serialize_deserialize_roundtrip(self, instance: Any) -> None:
        serializer = DataclassDtoSerializer(schema=type(instance))
        raw = serializer.serialize(instance)
        assert raw[:1] == DtoCodeEnum.DATACLASS
        restored = serializer.deserialize(raw)
        assert restored == instance
        assert isinstance(restored, type(instance))

    def test_deserialize_payload_raises_when_schema_is_none(
        self, dict_serializer: DictDtoSerializer
    ) -> None:
        serializer = DataclassDtoSerializer(schema=None)
        raw = b"\x02" + struct.pack("!I", 0) + b"{}"
        with pytest.raises(SerializerError, match="schema must be provided"):
            serializer.deserialize(raw)

    @pytest.mark.parametrize(
        "invalid_schema",
        [
            pytest.param({"key": "value"}, id="dict_instance"),
            pytest.param("not_a_type", id="string_instead_of_type"),
            pytest.param(42, id="int_instead_of_type"),
        ],
    )
    def test_deserialize_payload_raises_on_invalid_schema_type(self, invalid_schema: Any) -> None:
        serializer = DataclassDtoSerializer(schema=invalid_schema)
        raw = b"\x02" + struct.pack("!I", 2) + b"{}"
        with pytest.raises(SerializerError, match="given wrong schema for `dataclass` DTO"):
            serializer.deserialize(raw)

    def test_deserialize_handles_none_payload(
        self, dataclass_serializer: DataclassDtoSerializer
    ) -> None:
        assert dataclass_serializer.deserialize(None) is None
