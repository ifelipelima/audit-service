from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.routes.applications import router as applications_router
from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router

app = FastAPI(
    title="Audit Service",
    description="Serviço reutilizável de auditoria de eventos com Python e FastAPI, baseado em SOA.",
    version="0.1.0"
)


@app.exception_handler(OperationalError)
def database_unavailable_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Persistence service unavailable."},
    )


app.include_router(health_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
