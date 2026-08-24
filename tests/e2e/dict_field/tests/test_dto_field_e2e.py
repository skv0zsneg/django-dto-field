import struct

import pytest
from django.core.exceptions import ValidationError
from django.db import connection

from django_dto_field.dto.exceptions import DTOSerializeError
from django_dto_field.exceptions import BinaryDTOParserError
from dict_field.models import DataclassModel, DictModel, NullableModel, UserDTO


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

    instance = DataclassModel.objects.create(payload=UserDTO(2, "test@example.test"))
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE dict_field_dataclassmodel SET payload = %s WHERE id = %s",
            [b"\x01" + struct.pack("!I", 2) + b"{}", instance.pk],
        )
    with pytest.raises(DTOSerializeError, match="mismatch"):
        DataclassModel.objects.get(pk=instance.pk)
