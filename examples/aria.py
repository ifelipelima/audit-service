"""Consumidor de exemplo: Aria (gestão de documentos).

Outra aplicação, com outro domínio e outra API Key. Registra ações sobre um
documento, demonstra o conflito ao reutilizar um event_id e mostra que só
enxerga os próprios eventos.

Execução, a partir da raiz do repositório:
    AUDIT_URL=http://localhost:8000 ARIA_API_KEY=aud_... python -m examples.aria
"""

import os
from datetime import UTC, datetime
from uuid import uuid4

from client.audit_client import AuditClient, AuditClientError


def main() -> None:
    base_url = os.environ.get("AUDIT_URL", "http://localhost:8000")
    api_key = os.environ["ARIA_API_KEY"]
    document_id = f"doc-{uuid4().hex[:6]}"

    with AuditClient(base_url, api_key) as audit:
        for action, actor in [
            ("document.created", "ana"),
            ("document.shared", "ana"),
            ("document.signed", "bruno"),
        ]:
            audit.send_event({
                "event_id": f"aria-{uuid4()}",
                "actor_id": actor,
                "action": action,
                "resource_type": "document",
                "resource_id": document_id,
                "occurred_at": datetime.now(UTC).isoformat(),
            })
            print(f"Registrado: {action} por {actor}")

        # Mesmo event_id com conteúdo diferente: o serviço recusa (409).
        base = {
            "event_id": f"aria-{uuid4()}",
            "action": "document.archived",
            "resource_type": "document",
            "resource_id": document_id,
            "occurred_at": datetime.now(UTC).isoformat(),
        }
        audit.send_event(base)
        try:
            audit.send_event({**base, "action": "document.deleted"})
        except AuditClientError as exc:
            print(f"Conflito esperado ao reutilizar event_id: HTTP {exc.status_code}")

        page = audit.list_events(resource_type="document", limit=10)
        print(f"Últimos eventos de documentos da Aria ({len(page['items'])}):")
        for event in page["items"]:
            print(f"  {event['occurred_at']}  {event['action']}  {event['resource_id']}")


if __name__ == "__main__":
    main()
