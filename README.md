# Audit Service

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

**Serviço Reutilizável de Auditoria de Eventos**

O Audit Service é um serviço desenvolvido com Python e FastAPI, seguindo os princípios da Arquitetura Orientada a Serviços (SOA).

A solução tem o objetivo de centralizar o registro e a consulta de eventos de auditoria para diferentes aplicações, oferecendo uma API REST padronizada e independente dos sistemas consumidores.

O projeto é desenvolvido como parte da disciplina de Reuso de Software da Universidade Federal do Ceará (UFC) - Campus Quixadá.

---

### Pré-requisitos

[![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)](https://git-scm.com/downloads)
[![Python 3.12+](https://img.shields.io/badge/Python%203.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://docs.docker.com/get-docker/)

### Instalação e execução

**1. Clone o repositório**

```bash
git clone https://github.com/ifelipelima/audit-service.git
cd audit-service
```

**2. Crie o ambiente virtual**

```bash
py -m venv .venv
```

**3. Instale as dependências**

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

**4. Configure as variáveis de ambiente**

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Gere uma chave administrativa segura:

```bash
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
```

Adicione a chave gerada à variável `ADMIN_API_KEY` no arquivo `.env`.

**5. Inicie o PostgreSQL**

```bash
docker compose up -d db
```

**6. Aplique as migrações do banco de dados**

```bash
.\.venv\Scripts\python.exe -m alembic upgrade head
```

**7. Inicie a aplicação**

```bash
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

### Documentação da API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Testes

Execução dos testes automatizados com pytest:

```bash
.\.venv\Scripts\python.exe -m pytest -v
```

### Eventos de auditoria

Todas as rotas de eventos exigem o header `X-API-Key` com a chave recebida no cadastro da aplicação. A aplicação é identificada pela chave, nunca pelo corpo da requisição, e só enxerga os próprios eventos.

| Método | Endpoint | Resposta |
| --- | --- | --- |
| POST | `/api/v1/events` | `201` evento criado · `200` reenvio idêntico · `409` mesmo `event_id` com outro conteúdo |
| GET | `/api/v1/events` | Lista paginada, do mais recente para o mais antigo |
| GET | `/api/v1/events/{id}` | `200` evento · `404` inexistente ou de outra aplicação |

Filtros de `GET /api/v1/events`: `actor_id`, `action`, `resource_type`, `resource_id`, `occurred_from` e `occurred_to` (com fuso horário). Paginação: `limit` (padrão 20, máximo 100) e `offset` (padrão 0).

Se o banco estiver indisponível, a API responde `503`.

### Cliente reutilizável

O módulo `client/audit_client.py` encapsula as chamadas à API com HTTPX e repete automaticamente falhas transitórias (erros de rede e respostas `429`, `502`, `503` e `504`) com backoff exponencial. O reenvio usa o mesmo `event_id`, então o serviço não duplica o registro. Erros de validação e autenticação não são repetidos.

```python
from client.audit_client import AuditClient

with AuditClient("http://localhost:8000", api_key="aud_...") as audit:
    audit.send_event({
        "event_id": "evt-001",
        "actor_id": "user-25",
        "action": "occupation.ended",
        "resource_type": "occupation",
        "occurred_at": "2026-11-20T14:00:00Z",
    })
    audit.list_events(actor_id="user-25", limit=10)
```

### Exemplos de consumo

Dois consumidores independentes, cada um com a própria API Key, estão em `examples/`:

- `maneja.py`: registra a ocupação de um terreno, reenvia um evento para demonstrar a idempotência e consulta o histórico.
- `aria.py`: registra ações sobre um documento e demonstra o conflito ao reutilizar um `event_id`.

Cadastre as duas aplicações em `POST /api/v1/applications/` (com `X-Admin-Key`) e execute, a partir da raiz do repositório:

```bash
$env:MANEJA_API_KEY="aud_..."; .\.venv\Scripts\python.exe -m examples.maneja
$env:ARIA_API_KEY="aud_..."; .\.venv\Scripts\python.exe -m examples.aria
```

Para ver o retry em ação, pare o PostgreSQL (`docker compose stop db`) durante a execução: a API responde `503` e o cliente repete a chamada até o banco voltar ou as tentativas acabarem.
