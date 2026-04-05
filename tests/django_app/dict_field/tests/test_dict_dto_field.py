import pytest

from django_dto_field.exceptions import UnknownDtoType

from ..models import ModelForTest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value",
    [
        {},
        {"level1": {"level2": {"key": "value"}}},
        {
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "null": None,
        },
        {"key": "value", "nested": {"a": 1}},
    ],
)
def test_dict_dto_good_values(value):
    model = ModelForTest.objects.create(dict_dto_field=value)
    got_from_db = ModelForTest.objects.get(pk=model.pk)
    assert got_from_db.dict_dto_field == value


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_value",
    [
        "not a dict",
        123,
        3.14,
        ["list"],
        (1, 2),
    ],
)
def test_dict_dto_bad_values(invalid_value):
    with pytest.raises(UnknownDtoType):
        ModelForTest.objects.create(dict_dto_field=invalid_value)


@pytest.mark.django_db
def test_dict_dto_modifying_inplace():
    model = ModelForTest.objects.create(dict_dto_field={"a": 1})
    model.dict_dto_field["b"] = 2
    model.save()
    got_from_db = ModelForTest.objects.get(pk=model.pk)
    assert got_from_db.dict_dto_field == {"a": 1, "b": 2}
