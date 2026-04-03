from typing import TypedDict

import pytest

from django_dto_field.handler import DtoHandler


class TestTypedDictOne(TypedDict):
    first: str
    second: int


@pytest.mark.parametrize(
    "typed_dict_data",
    (
        {'first': "1", 'second': 2},
    ),
)
def test_typed_dict_one(typed_dict_data):
    typed_dict_dto = TestTypedDictOne(**typed_dict_data)
    dto_handler = DtoHandler()
    raw_dto = dto_handler.serialize(typed_dict_dto)
    restored_dto = dto_handler.deserialize(raw_dto)

    assert typed_dict_dto == restored_dto
