import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from backend.models.schemas import FiltrosRecomendacion

class RecommenderEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True)
        
        # 1. Pesos Prioritarios
        self.W_GENRE = 0.45
        self.W_TAGS = 0.30
        self.W_REVIEW = 0.15
        self.W_PRICE = 0.10

        self.review_map = {
            "Overwhelmingly Positive": 1.0, "Very Positive": 0.9,
            "Positive": 0.8, "Mostly Positive": 0.7, "Mixed": 0.5,
            "Mostly Negative": 0.3, "Negative": 0.2, "Very Negative": 0.1,
            "Overwhelmingly Negative": 0.0
        }

        self._preparar_matriz_caracteristicas()

    def _preparar_matriz_caracteristicas(self):
        print("Calculando matriz orientada a la ontología...")

        # A. Ontología: Géneros y Tags
        self.mlb_genres = MultiLabelBinarizer()
        self.mlb_tags = MultiLabelBinarizer()
        
        genres_vec = self.mlb_genres.fit_transform(self.df['Genres']) * self.W_GENRE
        tags_vec = self.mlb_tags.fit_transform(self.df['Tags']) * self.W_TAGS

        # B. Metadatos: Precio y Reseñas
        scaler = MinMaxScaler()
        precios_norm = scaler.fit_transform(self.df[['Price']])
        precios_vec = (1.0 - precios_norm) * self.W_PRICE

        reseñas_vec = self.df['resena_categoria'].map(self.review_map).values.reshape(-1, 1) * self.W_REVIEW

        # C. Fusión de la Matriz de Características (Solo 4 dimensiones conceptuales)
        self.features_matrix = np.hstack([
            genres_vec, 
            tags_vec, 
            reseñas_vec, 
            precios_vec
        ])
        print(f"Matriz terminada. Dimensiones: {self.features_matrix.shape}")

    def obtener_recomendaciones(self, filtros: FiltrosRecomendacion, top_n: int = 20):
        # 1. Filtros Estrictos (Constraints)
        mask = pd.Series(True, index=self.df.index)
        
        # Traza de depuración para la terminal
        print(f"Total juegos iniciales: {mask.sum()}")

        if filtros.anio_lanzamiento_min:
            mask &= (self.df['Release date'].dt.year >= filtros.anio_lanzamiento_min)
            print(f"Tras filtro año min: {mask.sum()}")
            
        if filtros.anio_lanzamiento_max:
            mask &= (self.df['Release date'].dt.year <= filtros.anio_lanzamiento_max)
            print(f"Tras filtro año max: {mask.sum()}")
            
        if filtros.solo_gratuitos:
            mask &= (self.df['es_gratuito'] == True)
            print(f"Tras filtro gratuitos: {mask.sum()}")
            
        if filtros.precio_maximo is not None:
            mask &= (self.df['Price'] <= filtros.precio_maximo)
            print(f"Tras filtro precio: {mask.sum()}")

        if filtros.resena_minima:
            # 1. Normalizamos el diccionario base (minúsculas y sin espacios)
            safe_map = {str(k).lower().strip(): float(v) for k, v in self.review_map.items()}
            
            # 2. Extraemos y normalizamos el valor del frontend (Pydantic Enum a String)
            texto_frontend = str(filtros.resena_minima.value).lower().strip()
            valor_minimo_deseado = safe_map.get(texto_frontend, 0.0)
            
            # 3. Normalizamos la columna completa del DataFrame
            columna_limpia = self.df['resena_categoria'].astype(str).str.lower().str.strip()
            
            # 4. Mapeamos a valores numéricos
            reseñas_numericas = columna_limpia.map(safe_map).fillna(0.0)
            
            # 5. Aplicamos la máscara final
            mask &= (reseñas_numericas >= valor_minimo_deseado)
            print(f"Tras filtro reseña (>= {valor_minimo_deseado}): {mask.sum()}")

        indices_filtrados = self.df[mask].index
        if len(indices_filtrados) == 0:
            print("ADVERTENCIA: Los filtros descartaron el 100% del catálogo.")
            return []

        # 2. Generación del Vector del Usuario
        user_genre_vec = self.mlb_genres.transform([filtros.generos_deseados]) * self.W_GENRE
        user_tag_vec = self.mlb_tags.transform([filtros.tags_deseados]) * self.W_TAGS
        
        target_review = self.review_map.get(str(filtros.resena_minima.value), 0.8) * self.W_REVIEW
        target_price = (1.0 if filtros.solo_gratuitos else 0.7) * self.W_PRICE

        user_vector = np.hstack([
            user_genre_vec, 
            user_tag_vec, 
            [[target_review]], 
            [[target_price]]
        ])

        # 3. Cálculo de Similitud
        matriz_candidatos = self.features_matrix[indices_filtrados]
        similitudes = cosine_similarity(user_vector, matriz_candidatos)[0]

        # 4. Post-procesamiento
        df_res = self.df.loc[indices_filtrados].copy()
        df_res['match_score'] = similitudes * 100
        
        recomendaciones = df_res.sort_values(by='match_score', ascending=False).head(top_n)
        
        recomendaciones = recomendaciones.rename(columns={
            'AppID': 'app_id', 'Name': 'titulo', 'Price': 'precio',
            'Release date': 'fecha_lanzamiento', 'resena_categoria': 'resena',
            'Genres': 'generos', 'Tags': 'tags'
        })
        
        recomendaciones['fecha_lanzamiento'] = recomendaciones['fecha_lanzamiento'].dt.date
        
        def validar_cardinalidad_tags(lista_tags):
            if isinstance(lista_tags, list) and len(lista_tags) > 0:
                return lista_tags
            return ["Sin etiquetas"]

        recomendaciones['tags'] = recomendaciones['tags'].apply(validar_cardinalidad_tags)

        recomendaciones['imagen_url'] = recomendaciones['app_id'].apply(
            lambda x: f"https://cdn.akamai.steamstatic.com/steam/apps/{x}/header.jpg"
        )

        return recomendaciones.to_dict('records')
    
    def obtener_recomendaciones_por_biblioteca(self, app_ids_usuario: list, top_n: int = 20):
        # 1. Identificar los juegos del usuario que existen en nuestro dataset local
        juegos_usuario = self.df[self.df['AppID'].isin(app_ids_usuario)]
        
        if juegos_usuario.empty:
            print("ADVERTENCIA: Ningún juego del usuario coincide con el dataset local.")
            return []

        # 2. Extraer los vectores de características de esos juegos
        indices_usuario = juegos_usuario.index
        vectores_usuario = self.features_matrix[indices_usuario]
        
        # 3. Calcular el centroide (Vector Promedio) del usuario
        # axis=0 suma las columnas, creando un único perfil consolidado
        perfil_usuario = np.mean(vectores_usuario, axis=0).reshape(1, -1)
        
        # 4. Calcular similitud contra todo el catálogo local
        similitudes = cosine_similarity(perfil_usuario, self.features_matrix)[0]
        
        # 5. Formateo y Exclusión
        df_res = self.df.copy()
        df_res['match_score'] = similitudes * 100
        
        # REGLA ESTRICTA: Excluir los juegos que el usuario ya posee
        df_res = df_res[~df_res['AppID'].isin(app_ids_usuario)]
        
        recomendaciones = df_res.sort_values(by='match_score', ascending=False).head(top_n)
        
        recomendaciones = recomendaciones.rename(columns={
            'AppID': 'app_id', 'Name': 'titulo', 'Price': 'precio',
            'Release date': 'fecha_lanzamiento', 'resena_categoria': 'resena',
            'Genres': 'generos', 'Tags': 'tags'
        })
        
        recomendaciones['fecha_lanzamiento'] = recomendaciones['fecha_lanzamiento'].dt.date
        
        def validar_cardinalidad_tags(lista_tags):
            if isinstance(lista_tags, list) and len(lista_tags) > 0:
                return lista_tags
            return ["Sin etiquetas"]

        recomendaciones['tags'] = recomendaciones['tags'].apply(validar_cardinalidad_tags)

        recomendaciones['imagen_url'] = recomendaciones['app_id'].apply(
            lambda x: f"https://cdn.akamai.steamstatic.com/steam/apps/{x}/header.jpg"
        )

        return recomendaciones.to_dict('records')