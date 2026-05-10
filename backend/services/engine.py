import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from typing import List
from backend.models.schemas import FiltrosRecomendacion

class RecommenderEngine:
    def __init__(self, df: pd.DataFrame):
        """
        Al instanciarse, prepara las matrices de géneros y etiquetas 
        para que las búsquedas posteriores sean instantáneas.
        """
        self.df = df
        self.mlb_genres = MultiLabelBinarizer()
        self.mlb_tags = MultiLabelBinarizer()
        
        # Creamos las matrices binarias (1s y 0s) para todo el catálogo
        print("Vectorizando catálogo de juegos...")
        genres_matrix = self.mlb_genres.fit_transform(self.df['Genres'])
        tags_matrix = self.mlb_tags.fit_transform(self.df['Tags'])
        
        # Combinamos géneros y etiquetas en una sola gran matriz de características
        self.features_matrix = np.hstack([genres_matrix, tags_matrix])
        print(f"Matriz de características lista: {self.features_matrix.shape}")

    def obtener_recomendaciones(self, filtros: FiltrosRecomendacion, top_n: int = 10):
        # 1. Aplicación de Filtros Duros (Constraints)
        # Primero reducimos el universo de búsqueda según precio, fecha y gratuidad
        mask = pd.Series(True, index=self.df.index)

        if filtros.solo_gratuitos:
            mask &= (self.df['es_gratuito'] == True)
        elif filtros.precio_maximo is not None:
            mask &= (self.df['Price'] <= filtros.precio_maximo)
            
        if filtros.anio_lanzamiento_min:
            mask &= (self.df['Release date'].dt.year >= filtros.anio_lanzamiento_min)
            
        if filtros.resena_minima:
            mask &= (self.df['resena_categoria'] == filtros.resena_minima)

        # Obtenemos los índices de los juegos que pasaron el filtro
        indices_filtrados = self.df[mask].index
        
        if len(indices_filtrados) == 0:
            return []

        # 2. Construcción del Vector de Preferencias del Usuario
        # Convertimos la selección del usuario (ej. ['RPG', 'Action']) al mismo formato binario
        user_genre_vec = self.mlb_genres.transform([filtros.generos_deseados])
        user_tag_vec = self.mlb_tags.transform([filtros.tags_deseados])
        user_vector = np.hstack([user_genre_vec, user_tag_vec])

        # 3. Cálculo de Similitud del Coseno
        # Solo comparamos el vector del usuario contra los juegos que pasaron los filtros iniciales
        matriz_candidatos = self.features_matrix[indices_filtrados]
        similitudes = cosine_similarity(user_vector, matriz_candidatos)[0]

        # 4. Formateo de Resultados
        df_resultados = self.df.loc[indices_filtrados].copy()
        df_resultados['match_score'] = similitudes * 100 # Escala 0-100
        
        # Ordenamos de mayor a menor coincidencia
        recomendaciones = df_resultados.sort_values(by='match_score', ascending=False).head(top_n)
        
        # Renombramos las columnas para que coincidan con los schemas de Pydantic
        recomendaciones = recomendaciones.rename(columns={
            'AppID': 'app_id',
            'Name': 'titulo',
            'Price': 'precio',
            'Release date': 'fecha_lanzamiento',
            'resena_categoria': 'resena',
            'Genres': 'generos',
            'Tags': 'tags'
        })

        # Convertimos el Timestamp de Pandas a un objeto date estándar de Python
        recomendaciones['fecha_lanzamiento'] = recomendaciones['fecha_lanzamiento'].dt.date

        # Aseguramos que ningún juego viole la regla ontológica de min 1 tag
        recomendaciones['tags'] = recomendaciones['tags'].apply(
            lambda x: ["Sin etiquetas"] if len(x) == 0 else x
        )
        
        # Mapeo final para cumplir con la respuesta de la API
        return recomendaciones.to_dict('records')