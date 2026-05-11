from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.api.endpoints import router as api_router
from backend.data.loader import DataLoader
from backend.services.engine import RecommenderEngine
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Esta función se ejecuta de forma asíncrona exactamente una vez 
    cuando el servidor arranca.
    """
    ruta_csv = "backend/data/games_limpio.csv"
    
    if not os.path.exists(ruta_csv):
        print(f"ERROR CRÍTICO: No se encuentra el archivo en {ruta_csv}")
        yield
        return
        
    # 1. Cargar y procesar datos
    loader = DataLoader(ruta_csv)
    df_procesado = loader.cargar_y_procesar()
    
    # 2. Inicializar el motor matemático y guardarlo en el estado de la app
    app.state.engine = RecommenderEngine(df_procesado)
    print("Servidor listo para recibir peticiones.")
    
    yield # Aquí el servidor se queda escuchando peticiones
    
    # Lo que va debajo del yield se ejecuta cuando el servidor se apaga
    app.state.engine = None
    print("Memoria liberada. Servidor apagado.")

# Inicialización de FastAPI con el ciclo de vida definido
app = FastAPI(
    title="Steam Recommender API", 
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto por defecto de Vite
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, etc.
    allow_headers=["*"],
)

# Integración del router de endpoints bajo el prefijo /api
app.include_router(api_router, prefix="/api")