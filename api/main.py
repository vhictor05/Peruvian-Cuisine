from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import settings

# Importar los routers
from api.routes import restaurant, hotel, disco, reports  # Quitamos auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema de Gestión Integrado para Dormilon Industries",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers (comentamos el router de auth)
# app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(restaurant.router, prefix=f"{settings.API_V1_STR}/restaurant", tags=["restaurant"])
app.include_router(hotel.router, prefix=f"{settings.API_V1_STR}/hotel", tags=["hotel"])
app.include_router(disco.router, prefix=f"{settings.API_V1_STR}/disco", tags=["disco"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])

@app.get("/")
async def root():
    return {
        "app_name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "running"
    }