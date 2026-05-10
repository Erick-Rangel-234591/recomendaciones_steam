from fastapi import APIRouter, HTTPException, Request
from backend.models.schemas import FiltrosRecomendacion, RespuestaRecomendacion

# Instanciamos el router
router = APIRouter()

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
        # Solicitamos el Top 10 de resultados
        resultados = engine.obtener_recomendaciones(filtros, top_n=10)
        
        # Formateamos la respuesta final
        return {
            "total_resultados": len(resultados),
            "recomendaciones": resultados
        }
    except Exception as e:
        # Captura de errores imprevistos en el cálculo matricial
        raise HTTPException(status_code=500, detail=f"Error interno del motor: {str(e)}")