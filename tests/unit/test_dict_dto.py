import pytest

from django_dto_field.handler import DtoHandler


@pytest.mark.parametrize(
    "dict_dto",
    (
        {"first": 1, "second": [2, 3]},
        {},
        {"wow": [{"inner_dict": {"another_one": 1}} for _ in range(100_000)]},
    ),
)
def test_good_dict_dto(dict_dto):
    dto_handler = DtoHandler()
    raw_dto = dto_handler.serialize(dict_dto)
    restored_dto = dto_handler.deserialize(raw_dto)

    assert dict_dto == restored_dto
