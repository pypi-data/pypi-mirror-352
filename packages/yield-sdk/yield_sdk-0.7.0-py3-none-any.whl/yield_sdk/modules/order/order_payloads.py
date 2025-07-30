import dataclasses as dc
import datetime as dt
import enum
import typing as t

import typing_extensions as tx

from yield_sdk.types import Money, MoneyLike, MoneyPayload
from yield_sdk.utils import type_utils


class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


@dc.dataclass(frozen=True, kw_only=True, slots=True)
class Order:
    id: str
    order_number: str
    status: OrderStatus
    customer: "OrderCustomerInfo | None"
    date: dt.date
    total_amount: Money
    note: str | None
    payment_link: str | None
    creation_time: dt.datetime

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "Order":
        return cls(
            id=type_utils.expect_string(payload["id"]),
            order_number=type_utils.expect_string(payload["order_number"]),
            status=OrderStatus(payload["status"]),
            customer=OrderCustomerInfo.from_payload(type_utils.expect_record(payload["customer"]))
            if payload.get("customer") is not None
            else None,
            date=type_utils.expect_date(payload["date"]),
            total_amount=Money.from_payload(type_utils.expect_string(payload["total_amount"])),
            note=type_utils.expect_string(payload["note"]) if payload.get("note") is not None else None,
            payment_link=type_utils.expect_string(payload["payment_link"])
            if payload.get("payment_link") is not None
            else None,
            creation_time=type_utils.expect_time(payload["creation_time"]),
        )


@dc.dataclass(frozen=True, kw_only=True, slots=True)
class OrderCustomerInfo:
    id: str
    registered_name: str
    trade_name: str | None
    customer_code: str | None

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "OrderCustomerInfo":
        return cls(
            id=type_utils.expect_string(payload["id"]),
            registered_name=type_utils.expect_string(payload["registered_name"]),
            trade_name=type_utils.expect_string(payload["trade_name"])
            if payload.get("trade_name") is not None
            else None,
            customer_code=type_utils.expect_string(payload["customer_code"])
            if payload.get("customer_code") is not None
            else None,
        )


class OrderCreateParams(t.TypedDict):
    customer_id: str
    total_amount: MoneyLike
    note: tx.NotRequired[str | None]


class OrderCreatePayload:
    @classmethod
    def build(cls, params: OrderCreateParams) -> dict[str, object]:
        return {
            "customer_id": params["customer_id"],
            "total_amount": MoneyPayload.build(params["total_amount"]),
            "note": params.get("note"),
        }
