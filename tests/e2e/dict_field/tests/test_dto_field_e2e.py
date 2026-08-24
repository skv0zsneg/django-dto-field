import struct

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection

from django_dto_field.dto.exceptions import DTOError, DTOSerializeError
from django_dto_field.exceptions import BinaryDTOParserError
from dict_field.models import (
    DataclassModel,
    DefaultDictModel,
    DictModel,
    NullableModel,
    UserDTO,
)


@pytest.mark.django_db
def test_dict_field_crud_bulk_update_and_mutation() -> None:
    instance = DictModel.objects.create(payload={"nested": [1, None]})
    instance.refresh_from_db()
    instance.payload["changed"] = True
    instance.save()
    assert DictModel.objects.get(pk=instance.pk).payload == {"nested": [1, None], "changed": True}

    DictModel.objects.bulk_create([DictModel(payload={"number": number}) for number in range(3)])
    assert {
        item["number"]
        for item in DictModel.objects.values_list("payload", flat=True)
        if "number" in item
    } == {0, 1, 2}


@pytest.mark.django_db
def test_dict_field_preserves_complex_values_through_orm_read_paths() -> None:
    payload = {
        "none": None,
        "boolean": True,
        "integer": -42,
        "float": 3.14,
        "unicode": "Hello, Django",
        "list": [0, False, {"nested": "value"}],
    }
    instance = DictModel.objects.create(payload=payload)

    assert DictModel.objects.values_list("payload", flat=True).get(pk=instance.pk) == payload
    assert DictModel.objects.only("payload").get(pk=instance.pk).payload == payload

    deferred = DictModel.objects.defer("payload").get(pk=instance.pk)
    assert deferred.get_deferred_fields() == {"payload"}
    assert deferred.payload == payload


@pytest.mark.django_db
def test_dict_field_supports_lookup_and_all_orm_update_paths() -> None:
    first = DictModel.objects.create(payload={"number": 1})
    second = DictModel.objects.create(payload={"number": 2})

    assert list(DictModel.objects.filter(payload={"number": 1})) == [first]
    assert list(
        DictModel.objects.filter(payload__in=[{"number": 1}, {"number": 2}]).order_by("pk")
    ) == [first, second]
    assert list(DictModel.objects.exclude(payload={"number": 1})) == [second]

    first.payload = {"number": 10}
    second.payload = {"number": 20}
    DictModel.objects.bulk_update([first, second], ["payload"])
    assert list(DictModel.objects.order_by("pk").values_list("payload", flat=True)) == [
        {"number": 10},
        {"number": 20},
    ]

    DictModel.objects.filter(pk=first.pk).update(payload={"number": 100})
    first.refresh_from_db(fields=["payload"])
    assert first.payload == {"number": 100}


@pytest.mark.django_db
def test_dict_field_default_is_serialized_and_not_shared_between_instances() -> None:
    first = DefaultDictModel.objects.create()
    second = DefaultDictModel.objects.create()

    assert first.payload == {"version": 1, "flags": []}
    assert second.payload == {"version": 1, "flags": []}

    first.payload["flags"].append("changed")
    first.save(update_fields=["payload"])
    second.refresh_from_db()

    assert first.payload == {"version": 1, "flags": ["changed"]}
    assert second.payload == {"version": 1, "flags": []}


@pytest.mark.django_db
def test_dataclass_and_nullable_fields_round_trip_and_validate() -> None:
    value = UserDTO(1, "ada@example.test", False)
    instance = DataclassModel.objects.create(payload=value)
    assert DataclassModel.objects.get(pk=instance.pk).payload == value

    nullable = NullableModel.objects.create(payload=None)
    nullable.payload = value
    nullable.save()
    assert NullableModel.objects.get(pk=nullable.pk).payload == value

    with pytest.raises(ValidationError, match="not valid"):
        DataclassModel(payload={"identifier": 1}).full_clean()


@pytest.mark.django_db(transaction=True)
def test_dataclass_schema_is_enforced_by_every_write_path() -> None:
    invalid_payload = {"identifier": 1, "email": "ada@example.test"}

    with pytest.raises(ValidationError, match="not valid"):
        DataclassModel.objects.create(payload=invalid_payload)
    with pytest.raises(ValidationError, match="not valid"):
        DataclassModel.objects.bulk_create([DataclassModel(payload=invalid_payload)])

    instance = DataclassModel.objects.create(payload=UserDTO(1, "ada@example.test"))
    with pytest.raises(ValidationError, match="not valid"):
        DataclassModel.objects.filter(pk=instance.pk).update(payload=invalid_payload)

    instance.refresh_from_db()
    assert instance.payload == UserDTO(1, "ada@example.test")


@pytest.mark.django_db
def test_dataclass_defaults_and_null_semantics_are_preserved() -> None:
    instance = DataclassModel.objects.create(payload=UserDTO(7, "default@example.test"))
    assert instance.payload.active is True
    assert DataclassModel.objects.get(pk=instance.pk).payload == UserDTO(
        7, "default@example.test", True
    )

    nullable = NullableModel.objects.create(payload=None)
    assert NullableModel.objects.values_list("payload", flat=True).get(pk=nullable.pk) is None
    nullable.full_clean()

    with pytest.raises(ValidationError, match="cannot be null"):
        DictModel(payload=None).full_clean()
    with pytest.raises(ValidationError, match="cannot be blank"):
        DictModel(payload=b"").full_clean()
    with pytest.raises(IntegrityError):
        DictModel.objects.create(payload=None)


@pytest.mark.django_db
def test_corrupted_and_wrong_schema_bytes_are_reported() -> None:
    instance = DictModel.objects.create(payload={})
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE dict_field_dictmodel SET payload = %s WHERE id = %s",
            [b"\x01" + struct.pack("!I", 4) + b"x", instance.pk],
        )
    with pytest.raises(BinaryDTOParserError, match="truncated"):
        DictModel.objects.get(pk=instance.pk)

    dataclass_instance = DataclassModel.objects.create(
        payload=UserDTO(2, "test@example.test")
    )
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE dict_field_dataclassmodel SET payload = %s WHERE id = %s",
            [b"\x01" + struct.pack("!I", 2) + b"{}", dataclass_instance.pk],
        )
    with pytest.raises(DTOSerializeError, match="mismatch"):
        DataclassModel.objects.get(pk=dataclass_instance.pk)


@pytest.mark.django_db
def test_unknown_dto_code_is_reported_when_schema_is_not_fixed() -> None:
    instance = DictModel.objects.create(payload={})
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE dict_field_dictmodel SET payload = %s WHERE id = %s",
            [b"\xff" + struct.pack("!I", 2) + b"{}", instance.pk],
        )

    with pytest.raises(DTOError, match="No DTO found for code"):
        DictModel.objects.get(pk=instance.pk)
