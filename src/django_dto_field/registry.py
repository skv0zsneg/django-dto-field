from typing import TYPE_CHECKING

from django_dto_field.exceptions import RegistryError

if TYPE_CHECKING:  # pragma: no cover
    from django_dto_field.serializer import BaseDtoSerializer


class Registry:
    """Global registry for storing something."""

    def __init__(self) -> None:
        self._serializers: dict[bytes, type["BaseDtoSerializer"]] = {}

    def save_serializer(
        self,
        code: bytes,
        serializer: type["BaseDtoSerializer"],
    ) -> None:
        self._serializers[code] = serializer

    def get_serializer(self, code: bytes) -> type["BaseDtoSerializer"]:
        try:
            return self._serializers[code]
        except KeyError:
            raise RegistryError(
                "Registry Serializer Error: no serializer associated to '%r' code."
                % code
            )


# TODO: Globals is bad. Need to do something with it.
registry = Registry()
