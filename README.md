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
