import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from ..models import ModelForTest


@pytest.mark.django_db
def test_empty_dict():
    """Test saving and retrieving an empty dict."""
    test_model = ModelForTest.objects.create(default_dict_field={})
    test_model.refresh_from_db()
    assert test_model.default_dict_field == {}


@pytest.mark.django_db
def test_nested_dict():
    """Test saving and retrieving a nested dictionary."""
    nested_value = {"level1": {"level2": {"key": "value"}}}
    test_model = ModelForTest.objects.create(default_dict_field=nested_value)
    test_model.refresh_from_db()
    assert test_model.default_dict_field == nested_value


@pytest.mark.django_db
def test_dict_with_various_types():
    """Test dict with various standard types (str, int, float, list, bool)."""
    value = {
        "string": "text",
        "integer": 42,
        "float": 3.14,
        "boolean": True,
        "list": [1, 2, 3],
        "null": None,
    }
    test_model = ModelForTest.objects.create(default_dict_field=value)
    test_model.refresh_from_db()
    assert test_model.default_dict_field == value


@pytest.mark.django_db
def test_invalid_type_raises_validation_error():
    """Test that non-dict value raises ValidationError."""
    model_1 = ModelForTest.objects.create(default_dict_field="not a dict")
    with pytest.raises(ValidationError):
        model_1.full_clean()

    model_2 = ModelForTest.objects.create(default_dict_field=123)
    with pytest.raises(ValidationError):
        model_2.full_clean()


@pytest.mark.django_db
def test_none_value_handling():
    """Test behavior when None is passed."""
    # Depending on your field settings (null=True or not), this may raise an error
    # Assuming the field is not nullable by default
    with pytest.raises(IntegrityError):
        ModelForTest.objects.create(default_dict_field=None)


@pytest.mark.django_db
def test_field_serialization_deserialization_consistency():
    """Ensure that serialization and deserialization are consistent."""
    original = {"key": "value", "nested": {"a": 1}}
    test_model = ModelForTest.objects.create(default_dict_field=original)
    test_model.refresh_from_db()
    assert test_model.default_dict_field == original


@pytest.mark.django_db
def test_modifying_dict_in_place():
    """Test that in-place modifications are saved correctly."""
    test_model = ModelForTest.objects.create(default_dict_field={"a": 1})
    test_model.default_dict_field["b"] = 2
    test_model.save()
    test_model.refresh_from_db()
    assert test_model.default_dict_field == {"a": 1, "b": 2}


@pytest.mark.django_db
def test_clear_dict():
    """Test clearing the dictionary."""
    test_model = ModelForTest.objects.create(default_dict_field={"a": 1})
    test_model.default_dict_field.clear()
    test_model.save()
    test_model.refresh_from_db()
    assert test_model.default_dict_field == {}
