from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import reports
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

# Ruta para verificar el estado del servicio
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.1"}

if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    
    # Optimizar número de procesos a utilizar
    num_cores = multiprocessing.cpu_count()
    print(f"Iniciando servidor con {num_cores} procesos")
    
    # Iniciar Uvicorn con múltiples procesos
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        workers=num_cores,
        log_level="info"
    )