import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import multiprocessing
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import reports
from routes import disco  # <-- Importar el router de disco
from routes import reports, hotel  # Agregar import de hotel
from routes import reports, restaurant
import time
from starlette.middleware.base import BaseHTTPMiddleware
from estructura.crud.trago_crud import TragoCRUD
from sqlalchemy.orm import sessionmaker
from Database.DB import engine

app = FastAPI(
    title="Peruvian Cuisine API",
    description="API REST para el sistema integrado de Restaurant, Hotel y Discoteca",
    version="1.0.1"
)

# Middleware para medir tiempo de respuesta
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        print(f"Tiempo de respuesta: {process_time:.4f} segundos")
        return response

# Añadir middleware
app.add_middleware(TimingMiddleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(reports.router)
app.include_router(disco.router)  # <-- Incluir el router de disco
app.include_router(hotel.router)  # Agregar rutas de hotel
app.include_router(restaurant.router)

# Ruta para verificar el estado del servicio
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "modules": ["reports", "hotel"]  # Actualizar módulos disponibles
    }

@app.on_event("startup")
def inicializar_tragos_startup():
    pass

# Ruta raíz
@app.get("/")
async def root():
    return {
        "message": "Peruvian Cuisine API", 
        "version": "1.0.1",
        "docs": "/docs"
    }

if __name__ == "__main__":

    
    # Optimizar número de procesos a utilizar
    num_cores = multiprocessing.cpu_count()
    workers = min(4, max(1, num_cores - 1))
    print("Iniciando servidor en modo desarrollo...")
    
    print(f"🚀 Iniciando servidor con {workers} workers")
    print(f"📡 API disponible en: http://localhost:8000")
    print(f"📖 Documentación en: http://localhost:8000/docs")
    
    uvicorn.run(
        "app:app", 
        host="127.0.0.1",
        port=8000, 
        reload=True,
        log_level="info"
    )