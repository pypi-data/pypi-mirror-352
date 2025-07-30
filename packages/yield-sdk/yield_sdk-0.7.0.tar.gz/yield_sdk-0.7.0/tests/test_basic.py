import os

import pytest
import urllib3

import yield_sdk


@pytest.fixture
def api_key():
    return os.environ["YIELD_API_KEY"]


@pytest.fixture
def base_url():
    return os.environ.get("YIELD_API_BASE_URL", "")


@pytest.fixture
def sync_http_client(base_url):
    verify_tls_certificates = not base_url or "localhost" not in base_url
    if not verify_tls_certificates:
        urllib3.disable_warnings()

    cert_reqs = "CERT_REQUIRED" if verify_tls_certificates else "CERT_NONE"
    pm = urllib3.PoolManager(cert_reqs=cert_reqs)

    return yield_sdk.http.Urllib3SyncHTTPClient(pm)
    # return yield_sdk.http.HTTPXSyncHTTPClient(httpx.Client(verify=verify_tls_certificates))


@pytest.fixture
def sync_client(api_key, base_url, sync_http_client):
    return yield_sdk.SyncClient(api_key, base_url=base_url, http_client=sync_http_client)


def test_connection(sync_client, api_key):
    info = sync_client.self.info()

    assert info.id == api_key.split(":")[0]
