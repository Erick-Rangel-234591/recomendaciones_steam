import pandas as pd

def eliminar_columnas_kaggle(ruta_entrada, ruta_salida):
    estructura_original = [
        'AppID', 'Name', 'Release date', 'Estimated owners', 'Peak CCU', 
        'Required age', 'Price', 'Discount', 'DLC count', 'About the game', 
        'Supported languages', 'Full audio languages', 'Reviews', 
        'Header image', 'Website', 'Support url', 'Support email', 
        'Windows', 'Mac', 'Linux', 'Metacritic score', 'Metacritic url', 
        'User score', 'Positive', 'Negative', 'Score rank', 'Achievements', 
        'Recommendations', 'Notes', 'Average playtime forever', 
        'Average playtime two weeks', 'Median playtime forever', 
        'Median playtime two weeks', 'Developers', 'Publishers', 
        'Categories', 'Genres', 'Tags', 'Screenshots', 'Movies'
    ]

    # Columnas para el sistema de recomendación
    columnas_finales = [
        'AppID', 'Name', 'Release date', 'Price', 'Reviews', 
        'Positive', 'Negative', 'Genres', 'Tags'
    ]

    try:    
        df = pd.read_csv(
            ruta_entrada, 
            names=estructura_original, 
            header=0, 
            low_memory=False
        )

        df_optimizado = df[columnas_finales].copy()

        df_optimizado.dropna(subset=['AppID', 'Name'], inplace=True)

        df_optimizado.to_csv(ruta_salida, index=False)
        
        print(f"Archivo guardado en: {ruta_salida}")
        print(f"Muestra de los primeros datos:\n{df_optimizado.head(3)}")

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    eliminar_columnas_kaggle("games.xls", "games_limpio.csv")