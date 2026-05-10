
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum

# ==========================================
# 1. ENUMS (Valores Restringidos)
# ==========================================

class ResenaEnum(str, Enum):
    """Categorías de reseñas oficiales de Steam."""
    OVERWHELMINGLY_POSITIVE = "Overwhelmingly Positive"
    VERY_POSITIVE = "Very Positive"
    POSITIVE = "Positive"
    MOSTLY_POSITIVE = "Mostly Positive"
    MIXED = "Mixed"
    MOSTLY_NEGATIVE = "Mostly Negative"
    NEGATIVE = "Negative"
    VERY_NEGATIVE = "Very Negative"
    OVERWHELMINGLY_NEGATIVE = "Overwhelmingly Negative"
    NO_REVIEWS = "No reviews"

# ==========================================
# 2. MODELOS DE LA ONTOLOGÍA (Entidades Core)
# ==========================================

class Tag(BaseModel):
    nombre: str

class Genero(BaseModel):
    nombre: str

class JuegoBase(BaseModel):
    """Atributos fundamentales de un juego (Ontología)."""
    app_id: int
    titulo: str
    precio: float = Field(..., ge=0, description="El costo debe ser mayor o igual a cero")
    fecha_lanzamiento: date
    resena: ResenaEnum
    es_gratuito: bool
    generos: List[str]  # Simplificado a List[str] para facilitar la respuesta JSON
    tags: List[str] = Field(..., min_items=1, max_items=3)

# ==========================================
# 3. MODELOS DE PETICIÓN (Request - Frontend a Backend)
# ==========================================

class FiltrosRecomendacion(BaseModel):
    """
    Datos que el frontend (React) enviará al usuario cuando
    ajuste los selectores en el panel de control.
    """
    precio_maximo: Optional[float] = Field(None, ge=0)
    anio_lanzamiento_min: Optional[int] = Field(None, ge=1990, le=2025)
    resena_minima: Optional[ResenaEnum] = None
    solo_gratuitos: Optional[bool] = False
    
    # El usuario seleccionará qué géneros y tags quiere buscar
    generos_deseados: List[str] = []
    tags_deseados: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "precio_maximo": 30.0,
                "solo_gratuitos": False,
                "generos_deseados": ["Action", "RPG"],
                "tags_deseados": ["Shooter"]
            }
        }

# ==========================================
# 4. MODELOS DE RESPUESTA (Response - Backend a Frontend)
# ==========================================

class JuegoRecomendado(JuegoBase):
    """
    Lo que el motor de recomendación devuelve al frontend.
    Hereda todo de JuegoBase y añade el porcentaje de compatibilidad.
    """
    match_score: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="Porcentaje de similitud con el perfil buscado"
    )

class RespuestaRecomendacion(BaseModel):
    """Contenedor final para la respuesta de la API."""
    total_resultados: int
    recomendaciones: List[JuegoRecomendado]