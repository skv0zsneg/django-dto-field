import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

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
def test_dictfield_good_values(value):
    model = ModelForTest.objects.create(default_dict_field=value)
    model.refresh_from_db()
    assert model.default_dict_field == value


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
def test_dictfield_bad_values(invalid_value):
    model = ModelForTest.objects.create(default_dict_field=invalid_value)
    with pytest.raises(ValidationError):
        model.full_clean()


@pytest.mark.django_db
def test_dictfield_None_value():
    with pytest.raises(IntegrityError):
        ModelForTest.objects.create(default_dict_field=None)


@pytest.mark.django_db
def test_dictfield_modifying_inplace():
    model = ModelForTest.objects.create(default_dict_field={"a": 1})
    model.default_dict_field["b"] = 2
    model.save()
    model.refresh_from_db()
    assert model.default_dict_field == {"a": 1, "b": 2}


@pytest.mark.django_db
def test_dictfield_clearing():
    model = ModelForTest.objects.create(default_dict_field={"a": 1})
    model.default_dict_field.clear()
    model.save()
    model.refresh_from_db()
    assert model.default_dict_field == {}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "value,expected",
    [
        ({"a": 1}, "{'a': 1}"),
        ({}, "{}"),
        ({"x": [1, 2]}, "{'x': [1, 2]}"),
    ],
)
def test_dictfield_value_to_string(value, expected):
    model = ModelForTest.objects.create(default_dict_field=value)
    field = model._meta.get_field("default_dict_field")
    assert field.value_to_string(model) == expected


@pytest.mark.django_db
def test_dictfield_from_db_value_none():
    field = ModelForTest._meta.get_field("default_dict_field")
    assert field.from_db_value(None, None) is None


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"a": 1},
        {"nested": {"x": 10}},
    ],
)
def test_dictfield_from_db_value_none_to_python_with_valid_dict(value):
    field = ModelForTest._meta.get_field("default_dict_field")
    assert field.to_python(value) == value
