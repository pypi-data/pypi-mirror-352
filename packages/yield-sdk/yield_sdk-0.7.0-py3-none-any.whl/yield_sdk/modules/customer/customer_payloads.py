import dataclasses as dc
import typing as t

import typing_extensions as tx

from yield_sdk.types import CursorLike, CursorPayload, Money
from yield_sdk.utils import type_utils


@dc.dataclass(frozen=True, kw_only=True, slots=True)
class CustomerRow:
    id: str
    registered_name: str
    trade_name: str | None
    customer_code: str | None
    credit_line: "CustomerCreditLineInfo | None"

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "CustomerRow":
        return cls(
            id=type_utils.expect_string(payload["id"]),
            registered_name=type_utils.expect_string(payload["registered_name"]),
            trade_name=type_utils.expect_string(payload["trade_name"])
            if payload.get("trade_name") is not None
            else None,
            customer_code=type_utils.expect_string(payload["customer_code"])
            if payload.get("customer_code") is not None
            else None,
            credit_line=CustomerCreditLineInfo.from_payload(type_utils.expect_record(payload["credit_line"]))
            if payload.get("credit_line") is not None
            else None,
        )


@dc.dataclass(frozen=True, kw_only=True, slots=True)
class CustomerCreditLineInfo:
    credit_limit: Money
    amount_available: Money

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "CustomerCreditLineInfo":
        return cls(
            credit_limit=Money.from_payload(type_utils.expect_string(payload["credit_limit"])),
            amount_available=Money.from_payload(type_utils.expect_string(payload["amount_available"])),
        )


class CustomerListParams(t.TypedDict):
    limit: tx.NotRequired[int | None]
    after: "tx.NotRequired[CursorLike | None]"
    customer_code: tx.NotRequired[str | None]
    extra_system_id: tx.NotRequired[str | None]


class CustomerListPayload:
    @classmethod
    def build(cls, params: CustomerListParams) -> dict[str, str | int | None]:
        return {
            "limit": params.get("limit"),
            "after": CursorPayload.build(params["after"])
            if "after" in params and params["after"] is not None
            else None,
            "customer_code": params.get("customer_code"),
            "extra_system_id": params.get("extra_system_id"),
        }
