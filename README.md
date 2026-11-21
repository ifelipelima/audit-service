# Audit Service

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

**Serviço Reutilizável de Auditoria de Eventos**

O Audit Service é um serviço desenvolvido com Python e FastAPI, seguindo os princípios da Arquitetura Orientada a Serviços (SOA).

A solução tem o objetivo de centralizar o registro e a consulta de eventos de auditoria para diferentes aplicações, oferecendo uma API REST padronizada e independente dos sistemas consumidores.

O projeto é desenvolvido como parte da disciplina de Reuso de Software da Universidade Federal do Ceará (UFC) - Campus Quixadá.

---

### Pré-requisitos

[![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)](https://git-scm.com/downloads)
[![Python 3.12+](https://img.shields.io/badge/Python%203.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/downloads/)

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

**4. Inicie a aplicação**

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
