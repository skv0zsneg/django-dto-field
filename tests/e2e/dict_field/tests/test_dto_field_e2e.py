import struct
from typing import Any

import pytest
from django.core.exceptions import ValidationError
from django.db import connection

from django_dto_field.exceptions import CorruptedDtoError, DtoHandlerError, SerializerError
from django_dto_field.dto_field import DTOField
from ..models import (
    DataclassModel,
    DictModel,
    NullableSchemaModel,
    UserDTO,
)


class TestDtoFieldDirectMethods:
    @pytest.fixture
    def schema_field(self) -> DTOField:
        return DTOField(schema=UserDTO)

    @pytest.fixture
    def no_schema_field(self) -> DTOField:
        return DTOField()

    def test_to_python_returns_none_on_none(self, schema_field: DTOField) -> None:
        assert schema_field.to_python(None) is None

    def test_to_python_skips_validation_when_no_schema(self, no_schema_field: DTOField) -> None:
        # Без схемы валидация не выполняется, возвращается значение как есть
        value = {"arbitrary": "data"}
        assert no_schema_field.to_python(value) is value

    def test_to_python_passes_valid_dataclass(self, schema_field: DTOField) -> None:
        dto = UserDTO(id=1, email="a@b.com")
        assert schema_field.to_python(dto) is dto

    @pytest.mark.parametrize(
        "invalid_value",
        [{"id": 1}, "string", 42, UserDTO(id=1, email="test") if False else object()],
    )
    def test_to_python_raises_validation_error_on_invalid(
        self, schema_field: DTOField, invalid_value: Any
    ) -> None:
        with pytest.raises(ValidationError, match="is not valid for schema"):
            schema_field.to_python(invalid_value)

    def test_from_db_value_returns_none_on_none(self, schema_field: DTOField) -> None:
        assert schema_field.from_db_value(None) is None

    def test_get_db_prep_value_returns_none_on_none(self, schema_field: DTOField) -> None:
        assert schema_field.get_db_prep_value(None) is None

    def test_get_db_prep_value_serializes_valid_dict(self, no_schema_field: DTOField) -> None:
        data = {"key": "value", "num": 42}
        raw = no_schema_field.get_db_prep_value(data)
        assert isinstance(raw, bytes)
        assert raw[:1] == b"\x01"  # DICT code

    def test_get_db_prep_value_serializes_valid_dataclass(self, schema_field: DTOField) -> None:
        dto = UserDTO(id=10, email="test@e2e.com")
        raw = schema_field.get_db_prep_value(dto)
        assert isinstance(raw, bytes)
        assert raw[:1] == b"\x02"  # DATACLASS code


@pytest.mark.django_db
class TestDtoFieldOrmIntegration:
    @pytest.mark.parametrize(
        "dict_payload",
        [
            {},
            {"level1": {"level2": {"deep": True}}},
            {"list": [1, None, "str", 3.14], "null": None},
            {f"{i}": f"{i+1}" for i in range(500)},  # Средний payload
        ],
    )
    def test_dict_crud_roundtrip(self, dict_payload: dict) -> None:
        instance = DictModel.objects.create(payload=dict_payload)
        instance.refresh_from_db()
        assert instance.payload == dict_payload

    @pytest.mark.parametrize(
        "dto_instance",
        [
            UserDTO(id=1, email="alice@dev.local"),
            UserDTO(id=2, email="bob@dev.local", is_active=False),
        ],
    )
    def test_dataclass_crud_roundtrip(self, dto_instance: UserDTO) -> None:
        instance = DataclassModel.objects.create(payload=dto_instance)
        instance.refresh_from_db()
        assert instance.payload == dto_instance
        assert isinstance(instance.payload, UserDTO)

    def test_nullable_field_handles_none(self) -> None:
        instance = NullableSchemaModel.objects.create(payload=None)
        instance.refresh_from_db()
        assert instance.payload is None

        instance.payload = UserDTO(id=99, email="update@test.com")
        instance.save()
        instance.refresh_from_db()
        assert isinstance(instance.payload, UserDTO)

    def test_inplace_mutation_and_save(self) -> None:
        instance = DictModel.objects.create(payload={"a": 1})
        instance.payload["b"] = 2
        instance.payload.pop("a")
        instance.save()

        fetched = DictModel.objects.get(pk=instance.pk)
        assert fetched.payload == {"b": 2}

    def test_bulk_create_and_update(self) -> None:
        dicts = [{"i": i} for i in range(10)]
        objs = [DictModel(payload=d) for d in dicts]
        DictModel.objects.bulk_create(objs)

        fetched = list(DictModel.objects.values_list("payload", flat=True))
        assert len(fetched) == 10
        assert all(isinstance(p, dict) for p in fetched)


@pytest.mark.django_db
class TestDtoFieldErrorPropagation:
    def test_serialize_invalid_type_raises_dto_handler_error(self) -> None:
        with pytest.raises(DtoHandlerError):
            DictModel.objects.create(payload="not_a_dict")

    def test_validation_error_bubbles_to_model_clean(self) -> None:
        obj = DataclassModel(payload={"invalid": "structure"})
        with pytest.raises(ValidationError, match="is not valid for schema"):
            obj.full_clean()

    def test_corrupted_db_bytes_raises_corrupted_dto_error(self) -> None:
        instance = NullableSchemaModel.objects.create(payload=None)
        corrupted = b"\x02" + struct.pack("!I", 999) + b"truncated"

        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE dict_field_nullableschemamodel SET payload = %s WHERE id = %s",
                [corrupted, instance.pk],
            )

        with pytest.raises(CorruptedDtoError):
            NullableSchemaModel.objects.get(pk=instance.pk)

    def test_wrong_serializer_code_raises_serializer_error(self) -> None:
        instance = DictModel.objects.create(payload={})
        wrong_code_bytes = b"\x02" + struct.pack("!I", 0)

        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE dict_field_dictmodel SET payload = %s WHERE id = %s",
                [wrong_code_bytes, instance.pk],
            )

        with pytest.raises(SerializerError):
            DictModel.objects.get(pk=instance.pk)

    def test_large_payload_roundtrip(self) -> None:
        large_dict = {"data": "x" * 1_000_000}
        instance = DictModel.objects.create(payload=large_dict)
        instance.refresh_from_db()
        assert instance.payload["data"] == "x" * 1_000_000
