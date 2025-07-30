[*← Return to index*](../index.md)

Customer module
===============

**Endpoints:**
- ![query](https://img.shields.io/badge/QUERY-green) [`list(params)`](#-listparams)

**Objects:**
- [`CustomerRow`](#customerrow)
- [`CustomerCreditLineInfo`](#customercreditlineinfo)


Endpoints
---------

### ![query](https://img.shields.io/badge/QUERY-green) `list(params)`

Provides the list of customers under your account, ordered by creation time (newest first).

```python
params = {"field": value, ...}
customers = client.customer.list(params)

# or pass them as keyword arguments
customers = client.customer.list(field=value, ...)

# or since the parameters are all optional
customers = client.customer.list()
```

**Returns:** `Page` of [`CustomerRow`](#customerrow)

**Parameters:**

- `params`: `dict` — See the fields right below.

| Field           | Required? | Type         | Description                                             |
| --------------- | --------- | ------------ | ------------------------------------------------------- |
| `limit`         | Optional  | `int`        | The maximum number of results to return. Default: `10`. |
| `after`         | Optional  | `CursorLike` | See docs on pagination.                                 |
| `customer_code` | Optional  | `str`        | Filter by customer code.                                |


Objects
-------

### `CustomerRow`

| Field             | Type                                                          | Description                                   |
| ----------------- | ------------------------------------------------------------- | --------------------------------------------- |
| `id`              | `str`                                                         | The ID of the customer.                       |
| `registered_name` | `str`                                                         | The official registered name of the customer. |
| `trade_name`      | `str` \| `None`                                               | The trade name of the customer.               |
| `customer_code`   | `str` \| `None`                                               | The customer code assigned to this customer.  |
| `credit_line`     | [`CustomerCreditLineInfo`](#customercreditlineinfo) \| `None` | The credit line of the customer.              |


### `CustomerCreditLineInfo`

| Field              | Type    | Description                                |
| ------------------ | ------- | ------------------------------------------ |
| `credit_limit`     | `Money` | The credit limit.                          |
| `amount_available` | `Money` | The amount available for this credit line. |
