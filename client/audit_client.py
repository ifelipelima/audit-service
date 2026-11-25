"""Cliente HTTP reutilizável para o Audit Service.

Uso:
    with AuditClient("http://localhost:8000", api_key="aud_...") as audit:
        audit.send_event({...})

Falhas transitórias (erros de rede e respostas 429, 502, 503 e 504) são
repetidas com backoff exponencial, sempre com o mesmo corpo e, portanto, o
mesmo event_id: o serviço é idempotente e não duplica o registro. Erros de
validação e autenticação não são repetidos.
"""

from typing import Any

import httpx
from tenacity import (
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

RETRYABLE_STATUS = {429, 502, 503, 504}


class AuditClientError(Exception):
    def __init__(self, status_code: int, detail: Any):
        super().__init__(f"Audit Service respondeu {status_code}: {detail}")
        self.status_code = status_code
        self.detail = detail


class RetryableResponseError(AuditClientError):
    pass


def _is_retryable(exc: BaseException) -> bool:
    return isinstance(exc, (httpx.TransportError, RetryableResponseError))


class AuditClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        timeout: float = 5.0,
        max_attempts: int = 4,
        backoff_multiplier: float = 0.5,
        backoff_max: float = 8.0,
        transport: httpx.BaseTransport | None = None,
    ):
        self._http = httpx.Client(
            base_url=f"{base_url.rstrip('/')}/api/v1",
            headers={"X-API-Key": api_key},
            timeout=timeout,
            transport=transport,
        )
        self._max_attempts = max_attempts
        self._wait = wait_exponential(multiplier=backoff_multiplier, max=backoff_max)

    def send_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Registra um evento. Retorna o registro criado ou o já existente."""
        return self._request("POST", "/events", json=event)

    def get_event(self, id: str) -> dict[str, Any]:
        return self._request("GET", f"/events/{id}")

    def list_events(self, **params: Any) -> dict[str, Any]:
        params = {k: v for k, v in params.items() if v is not None}
        return self._request("GET", "/events", params=params)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "AuditClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        retrying = Retrying(
            retry=retry_if_exception(_is_retryable),
            stop=stop_after_attempt(self._max_attempts),
            wait=self._wait,
            reraise=True,
        )
        for attempt in retrying:
            with attempt:
                return self._send_once(method, url, **kwargs)
        raise AssertionError("unreachable")  # pragma: no cover

    def _send_once(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        response = self._http.request(method, url, **kwargs)

        if response.is_success:
            return response.json()

        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = response.text

        if response.status_code in RETRYABLE_STATUS:
            raise RetryableResponseError(response.status_code, detail)
        raise AuditClientError(response.status_code, detail)
