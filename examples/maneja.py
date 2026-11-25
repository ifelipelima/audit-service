"""Consumidor de exemplo: Maneja (gestão de ocupação de terrenos).

Registra a ocupação de um terreno do início ao fim, reenvia um evento para
mostrar a idempotência e consulta o histórico da ocupação.

Execução, a partir da raiz do repositório:
    AUDIT_URL=http://localhost:8000 MANEJA_API_KEY=aud_... python -m examples.maneja
"""

import os
from datetime import UTC, datetime
from uuid import uuid4

from client.audit_client import AuditClient


def now() -> str:
    return datetime.now(UTC).isoformat()


def main() -> None:
    base_url = os.environ.get("AUDIT_URL", "http://localhost:8000")
    api_key = os.environ["MANEJA_API_KEY"]

    terrain_id = f"terrain-{uuid4().hex[:6]}"
    occupation_id = f"occ-{uuid4().hex[:6]}"

    with AuditClient(base_url, api_key) as audit:
        started = {
            "event_id": f"maneja-{uuid4()}",
            "actor_id": "user-25",
            "action": "occupation.started",
            "resource_type": "occupation",
            "resource_id": occupation_id,
            "occurred_at": now(),
            "details": {"terrain_id": terrain_id},
        }
        first = audit.send_event(started)
        print(f"Ocupação iniciada, registro {first['id']}")

        # Reenvio do mesmo evento (por exemplo, após um timeout): não duplica.
        again = audit.send_event(started)
        print(f"Reenvio devolveu o mesmo registro: {again['id'] == first['id']}")

        audit.send_event({
            "event_id": f"maneja-{uuid4()}",
            "actor_id": "user-25",
            "action": "occupation.ended",
            "resource_type": "occupation",
            "resource_id": occupation_id,
            "occurred_at": now(),
            "details": {"terrain_id": terrain_id, "reason": "harvest finished"},
        })

        history = audit.list_events(resource_id=occupation_id)
        print(f"Histórico da ocupação {occupation_id}:")
        for event in history["items"]:
            print(f"  {event['occurred_at']}  {event['action']}  por {event['actor_id']}")


if __name__ == "__main__":
    main()
