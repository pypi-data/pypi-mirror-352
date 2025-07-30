Yield SDK for Python [![PyPI - Version](https://img.shields.io/pypi/v/yield-sdk)](https://pypi.org/project/yield-sdk/)
====================

The official [Yield](https://www.paywithyield.com) SDK for Python.


Documentation
-------------

- [API reference](https://github.com/yield-tech/sdk-python/blob/main/docs/index.md)


Installation
------------

```sh
pip install yield-sdk
```


Usage
-----

```python
import yield_sdk
import os

# For security, don't save the actual key in your code or repo
client = yield_sdk.SyncClient(os.environ["YIELD_API_KEY"])

# Fetch an existing order
order = client.order.fetch("ord_...")
print(order.customer.registered_name)

# Or create a new one
new_order = client.order.create({
    "customer_id": "org_...",
    "total_amount": "PHP 1234.50",
    "note": "Test order from the Python SDK!",
})

# Don't forget to close the client when you won't use it anymore
client.close()
```

For more details, check out our [API reference](https://github.com/yield-tech/sdk-python/blob/main/docs/index.md).
