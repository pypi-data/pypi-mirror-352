[*← Return to index*](../index.md)

Order module
============

**Endpoints:**
- ![query](https://img.shields.io/badge/QUERY-green) [`fetch(id)`](#-fetchid)
- ![command](https://img.shields.io/badge/COMMAND-orange) [`create(params)`](#-createparams)

**Objects:**
- [`Order`](#order)
- [`OrderStatus`](#orderstatus)
- [`OrderCustomerInfo`](#ordercustomerinfo)


Endpoints
---------

### ![query](https://img.shields.io/badge/QUERY-green) `fetch(id)`

Provides information about the order specified.

```python
order = client.order.fetch(id)
```

**Returns:** [Order](#order)

**Parameters:**

- `id`: `str` — The ID of the order.


### ![command](https://img.shields.io/badge/COMMAND-orange) `create(params)`

Creates a new order.

```python
params = {"field": value, ...}
order = client.order.create(params)
```

**Returns:** [`Order`](#order) — The newly created order.

**Parameters:**

- `params`: `dict` — See the fields right below.

| Field          | Required? | Type        | Description                                                                    |
| -------------- | --------- | ----------- | ------------------------------------------------------------------------------ |
| `customer_id`  | Required* | `str`       | The (Yield) customer ID that this order will belong to.                        |
| `total_amount` | Required  | `MoneyLike` | The total amount of the order.                                                 |
| `note`         | Required* | `str`       | A note shown to the customer during checkout, such as details about the order. |

\* These fields may become optional in a future release.


Objects
-------

### `Order`

| Field           | Type                                                | Description                                                                                    |
| --------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `id`            | `str`                                               | The ID of the order.                                                                           |
| `order_number`  | `str`                                               | The order number.                                                                              |
| `status`        | [`OrderStatus`](#orderstatus)                       | The status of the order.                                                                       |
| `customer`      | [`OrderCustomerInfo`](#ordercustomerinfo) \| `None` | The customer this order belongs to.                                                            |
| `date`          | `datetime.date`                                     | The date of the order.                                                                         |
| `total_amount`  | `Money`                                             | The total amount of the order.                                                                 |
| `note`          | `str` \| `None`                                     | A note shown to the customer during checkout, such as details about the order.                 |
| `payment_link`  | `str` \| `None`                                     | The payment link for the customer to confirm this order. May be `None` if no longer available. |
| `creation_time` | `datetime.datetime`                                 | The timestamp when this order was created.                                                     |


### `OrderStatus`

| Value                   | Description                                                                             |
| ----------------------- | --------------------------------------------------------------------------------------- |
| `OrderStatus.PENDING`   | The initial status for newly created orders. The customer has yet to confirm the order. |
| `OrderStatus.CONFIRMED` | The customer has confirmed the order.                                                   |
| `OrderStatus.FULFILLED` | The order has been marked as fulfilled.                                                 |
| `OrderStatus.CANCELLED` | The order has been cancelled.                                                           |


### `OrderCustomerInfo`

| Field             | Type            | Description                                   |
| ----------------- | --------------- | --------------------------------------------- |
| `id`              | `str`           | The ID of the customer.                       |
| `registered_name` | `str`           | The official registered name of the customer. |
| `trade_name`      | `str` \| `None` | The trade name of the customer.               |
| `customer_code`   | `str` \| `None` | The customer code assigned to this customer.  |
