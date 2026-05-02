import pytest
from typing import ClassVar

from django_dto_field.exceptions import DtoFeatureError
from django_dto_field.features.base import BaseDtoFeature, DtoCodeEnum


class TestBaseDtoFeature:
    def test_get_dto_code_on_base_class_raises(self) -> None:
        with pytest.raises(DtoFeatureError, match="missing definition of `dto_code`"):
            BaseDtoFeature._get_dto_code()

    def test_concrete_subclass_instantiates_successfully(self) -> None:
        class ValidFeature(BaseDtoFeature):
            dto_code: ClassVar[bytes] = DtoCodeEnum.DICT

        instance = ValidFeature()
        assert instance._get_dto_code() == DtoCodeEnum.DICT
        assert ValidFeature._get_dto_code() == DtoCodeEnum.DICT

    def test_init_implicitly_validates_dto_code(self) -> None:
        class InvalidFeature(BaseDtoFeature):
            dto_code: ClassVar[bytes | None] = None

        with pytest.raises(DtoFeatureError, match="missing definition of `dto_code`"):
            InvalidFeature()

    def test_get_dto_code_accessible_via_instance(self) -> None:
        class FeatureWithCode(BaseDtoFeature):
            dto_code: ClassVar[bytes] = b"\x0a"

        instance = FeatureWithCode()
        assert instance._get_dto_code() == b"\x0a"
