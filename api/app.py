from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import reports, restaurant
import time
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(
    title="Peruvian Cuisine API",
    description="API REST para el sistema integrado de Restaurant, Hotel y Discoteca",
    version="1.0.1"
)

# Middleware para medir tiempo de respuesta
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
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
app.include_router(restaurant.router)

# Ruta para verificar el estado del servicio
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.1"}

# Ruta raíz
@app.get("/")
async def root():
    return {
        "message": "Peruvian Cuisine API", 
        "version": "1.0.1",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("Iniciando servidor en modo desarrollo...")
    
    uvicorn.run(
        "app:app", 
        host="127.0.0.1",
        port=8000, 
        reload=True,
        log_level="info"
    )