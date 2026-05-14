import pandas as pd
import ast
from datetime import datetime

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    def cargar_y_procesar(self):
        """
        Carga el CSV y aplica las transformaciones necesarias para 
        cumplir con la ontología y preparar el motor de recomendación.
        """
        print(f"Cargando datos desde {self.file_path}...")
        self.df = pd.read_csv(self.file_path)
        
        self.df = self.df[~((self.df['Positive'] == 0) & (self.df['Negative'] == 0))]

        # 1. Procesar Fechas
        self.df['Release date'] = pd.to_datetime(self.df['Release date'], errors='coerce')
        # Llenar fechas nulas con una fecha muy antigua para evitar errores
        self.df['Release date'] = self.df['Release date'].fillna(datetime(1970, 1, 1))

        # 2. Determinar si es Gratuito (xsd:boolean)
        self.df['es_gratuito'] = self.df['Price'] == 0

        # 3. Clasificar Reseñas (steam:resena)
        self.df['resena_categoria'] = self.df.apply(self._calcular_categoria_resena, axis=1)

        # 4. Convertir Tags y Géneros a Listas
        self.df['Genres'] = self.df['Genres'].apply(self._limpiar_listas)
        self.df['Tags'] = self.df['Tags'].apply(self._limpiar_listas)

        # 5. Limitar tags
        # max 3 tags por regla de ontologia
        self.df['Tags'] = self.df['Tags'].apply(lambda x: x[:3])

        print(f"Procesamiento completado. {len(self.df)} juegos listos.")
        return self.df

    def _calcular_categoria_resena(self, row):
        """Calcula la categoría de reseña basada en el total y el % de positivos."""
        pos = row['Positive']
        neg = row['Negative']
        total = pos + neg
        
        porcentaje_pos = (pos / total) * 100

        if porcentaje_pos >= 95 and total >= 500:
            return "Overwhelmingly Positive"
        elif porcentaje_pos >= 80 and total >= 50:
            return "Very Positive"
        elif porcentaje_pos >= 80:
            return "Positive"
        elif porcentaje_pos >= 70:
            return "Mostly Positive"
        elif porcentaje_pos >= 40:
            return "Mixed"
        elif porcentaje_pos >= 20:
            return "Mostly Negative"
        elif total >= 500:
            return "Overwhelmingly Negative"
        elif total >= 50:
            return "Very Negative"
        else:
            return "Negative"

    def _limpiar_listas(self, x):
        """Convierte strings de texto en listas de Python."""
        if pd.isna(x):
            return []
        
        if isinstance(x, list):
            return x
        
        if x.startswith('['):
            try: return ast.literal_eval(x)
            except: return []
        
        return [item.strip() for item in x.replace(';', ',').split(',')]