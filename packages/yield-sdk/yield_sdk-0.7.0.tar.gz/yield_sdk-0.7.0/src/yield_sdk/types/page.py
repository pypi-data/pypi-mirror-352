import typing as t
from collections.abc import Callable

import typing_extensions as tx

from yield_sdk.utils import type_utils

T = t.TypeVar("T")
E = t.TypeVar("E")


class Page(t.Generic[T]):
    _items: list[T]
    _has_more: bool

    def __init__(self, items: list[T], has_more: bool):
        self._items = items
        self._has_more = has_more

    @classmethod
    def build_with(cls, from_payload: Callable[[dict[str, object]], E]) -> "Callable[[dict[str, object]], Page[E]]":
        def builder(payload: dict[str, object]):
            return Page(
                items=[from_payload(it) for it in type_utils.expect_record_list(payload["items"])],
                has_more=type_utils.expect_boolean(payload["has_more"]),
            )

        return builder

    @property
    def has_more(self):
        return self._has_more

    @tx.override
    def __repr__(self):
        return f"{type(self).__name__}(items={self._items!r}, has_more={self._has_more!r})"

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index: int):
        return self._items[index]

    def __iter__(self):
        return iter(self._items)
