from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.applications import router as applications_router

app = FastAPI(
    title="Audit Service",
    description="Serviço reutilizável de auditoria de eventos com Python e FastAPI, baseado em SOA.",
    version="0.1.0"
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")