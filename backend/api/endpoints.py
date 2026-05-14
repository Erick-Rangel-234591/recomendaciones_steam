from fastapi import APIRouter, HTTPException, Request
from backend.models.schemas import FiltrosRecomendacion, RespuestaRecomendacion
from backend.services.steam_client import SteamAPIClient 

# Instanciamos el router
router = APIRouter()

@router.get("/catalog/genres")
def get_available_genres(request: Request):
    """Devuelve la lista de géneros disponibles en el catálogo."""
    engine = request.app.state.engine
    if not engine:
        raise HTTPException(status_code=503, detail="Motor de recomendación no inicializado.")
    return {"genres": list(engine.mlb_genres.classes_)}

@router.get("/catalog/tags")
def get_available_tags(request: Request):
    """Devuelve la lista de tags disponibles en el catálogo."""
    engine = request.app.state.engine
    if not engine:
        raise HTTPException(status_code=503, detail="Motor de recomendación no inicializado.")
    return {"tags": list(engine.mlb_tags.classes_)}

@router.post("/recomendaciones/caracteristicas", response_model=RespuestaRecomendacion)
def recomendar_por_caracteristicas(filtros: FiltrosRecomendacion, request: Request):
    """
    Recibe los filtros del usuario, consulta el motor de recomendación en memoria
    y devuelve el Top de juegos que mejor coinciden.
    """
    # Extraemos el motor de recomendación de la memoria global de la aplicación
    engine = request.app.state.engine
    
    if not engine:
        raise HTTPException(status_code=503, detail="El motor de recomendación no está inicializado.")

    try:
        # Llamamos a la función de Similitud del Coseno que construimos en el engine.py
        # Solicitamos el Top n de resultados
        resultados = engine.obtener_recomendaciones(filtros, top_n=10)
        
        # Formateamos la respuesta final
        return {
            "total_resultados": len(resultados),
            "recomendaciones": resultados
        }
    except Exception as e:
        # Captura de errores imprevistos en el cálculo matricial
        raise HTTPException(status_code=500, detail=f"Error interno del motor: {str(e)}")
    
    
@router.get("/recomendaciones/biblioteca/{steam_id}", response_model=dict)
def recomendar_por_biblioteca(steam_id: str, request: Request):
    """
    Consume la API oficial de Steam para obtener la biblioteca del usuario
    y devuelve recomendaciones basadas en el perfil de sus juegos actuales.
    """
    engine = request.app.state.engine
    if not engine:
        raise HTTPException(status_code=500, detail="Motor de recomendación no inicializado.")

    try:
        # 1. Instanciar el cliente y consultar los servidores de Valve
        cliente_steam = SteamAPIClient()
        app_ids = cliente_steam.obtener_biblioteca_usuario(steam_id)
        
        # 2. Generar recomendaciones matemáticas
        resultados = engine.obtener_recomendaciones_por_biblioteca(app_ids)
        
        if not resultados:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron recomendaciones. La biblioteca del usuario es incompatible con el catálogo local."
            )
            
        return {
            "steam_id_consultado": steam_id,
            "total_juegos_analizados": len(app_ids),
            "total_resultados": len(resultados),
            "recomendaciones": resultados
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))