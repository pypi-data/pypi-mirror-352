import typing_extensions as tx

from yield_sdk.api_client import SyncAPIClient
from yield_sdk.api_result import APIResult
from yield_sdk.types import Page

from . import customer_payloads as payloads


class SyncCustomerClient:
    _base: "SyncCustomerBaseClient"

    def __init__(self, base_client: "SyncCustomerBaseClient"):
        self._base = base_client

    def list(
        self, params: payloads.CustomerListParams | None = None, **kwargs: tx.Unpack[payloads.CustomerListParams]
    ) -> Page[payloads.CustomerRow]:
        return self._base.list(params, **kwargs).data


class SyncCustomerBaseClient:
    _api: SyncAPIClient

    def __init__(self, api_client: SyncAPIClient):
        self._api = api_client

    def list(
        self, params: payloads.CustomerListParams | None = None, **kwargs: tx.Unpack[payloads.CustomerListParams]
    ) -> APIResult[Page[payloads.CustomerRow]]:
        merged = params | kwargs if params else kwargs
        payload = payloads.CustomerListPayload.build(merged) if merged else None
        response = self._api.run_query("/customer/list", payload)

        return SyncAPIClient.process_response(response, Page.build_with(payloads.CustomerRow.from_payload))
