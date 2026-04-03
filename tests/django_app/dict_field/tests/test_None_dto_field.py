import pytest

from ..models import ModelForTest


@pytest.mark.django_db
def test_None_dto_good_values():
    model = ModelForTest.objects.create(none_dto_field=None)
    got_from_db = ModelForTest.objects.get(pk=model.pk)
    assert got_from_db.none_dto_field is None
