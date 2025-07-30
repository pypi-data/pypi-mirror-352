import base64
import datetime as dt
import hmac
import json
import typing as t
import urllib.parse
from collections.abc import Callable, Mapping

from . import http, version
from .api_result import APIResult
from .utils import import_utils, type_utils

T = t.TypeVar("T")


class SyncAPIClient:
    _base_url: str

    _api_key_token: str
    _api_key_hmac_key: bytes

    _http: http.SyncHTTPClient
    _client_version: str

    def __init__(self, api_key: str, *, base_url: str = "", http_client: http.SyncHTTPClient | None = None):
        self._base_url = base_url or "https://integrate.withyield.com/api/v1"
        (self._api_key_token, self._api_key_hmac_key) = SyncAPIClient.extract_api_key(api_key)
        self._http = http_client if http_client else SyncAPIClient.find_http_client()
        self._client_version = version.get_client_version()

    @classmethod
    def extract_api_key(cls, key: str) -> tuple[str, bytes]:
        # "$" is the old separator, supported for backwards compatibility
        key_parts = key.replace("$", ":").split(":")
        if len(key_parts) != 3:
            raise ValueError("Invalid Yield API key")

        [key_id, key_secret, hmac_key_b64] = key_parts
        token = f"{key_id}${key_secret}"
        # Python's base64 throws when padding is missing, but trims extra padding
        hmac_key_bytes = base64.urlsafe_b64decode(hmac_key_b64 + "==")

        return (token, hmac_key_bytes)

    @classmethod
    def find_http_client(cls) -> http.SyncHTTPClient:
        if urllib3 := import_utils.try_import("urllib3"):  # This also covers requests (which uses urllib3)
            return http.Urllib3SyncHTTPClient(urllib3.PoolManager())
        elif httpx := import_utils.try_import("httpx"):
            return http.HTTPXSyncHTTPClient(httpx.Client())
        else:
            raise ValueError("No HTTP client found. Try installing `urllib3` or `httpx`.")

    @classmethod
    def build_signature(cls, hmac_key: bytes, timestamp: str, path: str, body: str | None = None) -> str:
        parts = [timestamp, path] if body is None else [timestamp, path, body]
        message = "\n".join(parts).encode()
        sig_bytes = hmac.digest(hmac_key, message, "sha512")

        return base64.urlsafe_b64encode(sig_bytes).rstrip(b"=").decode("utf-8")

    @classmethod
    def process_response(
        cls, response: http.Response, from_payload: Callable[[dict[str, object]], T]
    ) -> "APIResult[T]":
        status_code, headers, body = response
        ok = 200 <= status_code <= 299

        request_id = headers.get("X-Request-Id")

        if not ok:
            error_type = "unexpected_error"
            error_body = None
            try:
                error_body = type_utils.expect_record(json.loads(body))
                if isinstance(error_body["error"], str):
                    error_type = error_body["error"]
            except Exception:
                # ignore
                pass

            return APIResult.failure(status_code, request_id, error_type, error_body, None)

        try:
            payload = type_utils.expect_record(json.loads(body))
            data = from_payload(payload)
        except Exception as e:
            return APIResult.failure(status_code, request_id, "invalid_response", None, e)

        return APIResult.success(status_code, request_id, data)  # pyright: ignore

    def close(self) -> None:
        self._http.close()

    def run_query(self, path: str, params: Mapping[str, str | int | None] | None = None) -> http.Response:
        full_path = path
        if params:
            query_string = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if query_string:
                full_path += f"?{query_string}"

        return self._call_endpoint("GET", full_path, None)

    def run_command(self, path: str, payload: object) -> http.Response:
        return self._call_endpoint("POST", path, payload)

    def _call_endpoint(self, method: t.Literal["GET"] | t.Literal["POST"], path: str, payload: object) -> http.Response:
        headers = {"X-Yield-Client": self._client_version}

        body = None if payload is None else json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        if body is not None:
            headers["Content-Type"] = "application/json"

        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        signature = self.build_signature(self._api_key_hmac_key, timestamp, path, body)
        headers["Authorization"] = f"Yield-Sig {self._api_key_token}${timestamp}${signature}"

        return self._http.request(method, self._base_url + path, headers, body)
