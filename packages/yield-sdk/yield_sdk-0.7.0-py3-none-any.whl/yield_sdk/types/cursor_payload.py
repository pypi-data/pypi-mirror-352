import typing as t

from .page import Page

CursorLike: t.TypeAlias = "str | EntityProtocol | Page[EntityProtocol]"


class EntityProtocol(t.Protocol):
    @property
    def id(self) -> str: ...


class CursorPayload:
    @classmethod
    def build(cls, cursor: CursorLike) -> str | None:
        if isinstance(cursor, str):
            return cursor
        elif isinstance(cursor, Page):
            last = cursor[-1] if cursor else None

            return last.id if last else None
        else:
            return cursor.id
