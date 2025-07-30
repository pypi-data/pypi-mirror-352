from . import http
from . import modules as m
from .api_client import SyncAPIClient


class SyncClient:
    _base: "SyncBaseClient"

    _customer: m.customer.SyncCustomerClient
    _order: m.order.SyncOrderClient
    _self: m.self.SyncSelfClient

    def __init__(self, api_key: str, base_url: str = "", http_client: http.SyncHTTPClient | None = None):
        self._base = SyncBaseClient(api_key, base_url=base_url, http_client=http_client)

        self._customer = m.customer.SyncCustomerClient(self._base.customer)
        self._order = m.order.SyncOrderClient(self._base.order)
        self._self = m.self.SyncSelfClient(self._base.self)

    @property
    def base(self) -> "SyncBaseClient":
        return self._base

    @property
    def customer(self) -> m.customer.SyncCustomerClient:
        return self._customer

    @property
    def order(self) -> m.order.SyncOrderClient:
        return self._order

    @property
    def self(self) -> m.self.SyncSelfClient:
        return self._self

    def close(self) -> None:
        self._base.close()


class SyncBaseClient:
    _api: SyncAPIClient

    _customer: m.customer.SyncCustomerBaseClient
    _order: m.order.SyncOrderBaseClient
    _self: m.self.SyncSelfBaseClient

    def __init__(self, api_key: str, *, base_url: str = "", http_client: http.SyncHTTPClient | None = None):
        self._api = SyncAPIClient(api_key, base_url=base_url, http_client=http_client)

        self._customer = m.customer.SyncCustomerBaseClient(self._api)
        self._order = m.order.SyncOrderBaseClient(self._api)
        self._self = m.self.SyncSelfBaseClient(self._api)

    @property
    def api(self) -> SyncAPIClient:
        return self._api

    @property
    def customer(self) -> m.customer.SyncCustomerBaseClient:
        return self._customer

    @property
    def order(self) -> m.order.SyncOrderBaseClient:
        return self._order

    @property
    def self(self) -> m.self.SyncSelfBaseClient:
        return self._self

    def close(self) -> None:
        self._api.close()
