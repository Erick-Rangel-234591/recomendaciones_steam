# Steam Discovery Engine: Documentación Técnica y Fundamentos Matemáticos

Este proyecto implementa un sistema de recomendación híbrido basado en contenido que opera sobre un espacio vectorial de alta dimensionalidad. El motor procesa metadatos de más de 80,000 videojuegos para calcular afinidades semánticas mediante álgebra lineal.

## 1. El Modelo Matemático: Similitud del Coseno

El núcleo del motor utiliza la **Similitud del Coseno** para medir la cercanía entre dos vectores en un espacio multidimensional. A diferencia de la distancia euclidiana (que mide la longitud física entre puntos), la similitud del coseno mide el ángulo entre dos vectores, lo que la hace ideal para comparar perfiles de juegos independientemente de la cantidad de etiquetas que posean.

La ecuación fundamental es:

$$\text{similitud}(\mathbf{A}, \mathbf{B}) = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$

Donde:
* $\mathbf{A} \cdot \mathbf{B}$ es el producto punto de los vectores.
* $\|\mathbf{A}\| \|\mathbf{B}\|$ es el producto de sus normas (magnitudes).
* El resultado oscila entre **0** (ortogonalidad total/sin similitud) y **1** (vectores idénticos).

## 2. Arquitectura de Pesos (Ontología Ponderada)

No todas las características de un juego tienen el mismo valor semántico. El sistema aplica una **Matriz de Pesos Estructurales** para priorizar la ontología (géneros) sobre las etiquetas descriptivas (tags). Los pesos configurados son:

| Dimensión | Peso ($W$) | Descripción |
| :--- | :--- | :--- |
| **Géneros** | **45%** | Estructura fundamental del juego (ej. RPG, Action). |
| **Tags** | **30%** | Características descriptivas (ej. Open World, Soulslike). |
| **Reseñas** | **15%** | Factor de calidad externa (Validación de la comunidad). |
| **Precio** | **10%** | Factor de accesibilidad económica. |

El vector de características final $\mathbf{V}_{final}$ se construye como la concatenación ponderada de sub-vectores:
$$\mathbf{V}_{final} = [ ( \vec{V}_{g} \cdot 0.45 ), ( \vec{V}_{t} \cdot 0.30 ), ( \vec{V}_{r} \cdot 0.15 ), ( \vec{V}_{p} \cdot 0.10 ) ]$$

## 3. Flujos de Generación de Vectores

El motor es capaz de generar el vector de entrada de dos formas distintas antes de realizar la comparación:

### A. Perfilado por Características (Vector Sintético)
El usuario define parámetros explícitos. El sistema crea un vector "ideal" en tiempo real donde los bits correspondientes a los géneros y tags seleccionados se activan ($1$), y el resto permanece en $0$.

### B. Perfilado por Biblioteca (Vector Centroide)
Para recomendaciones basadas en el historial de Steam, el sistema calcula el **Centroide del Usuario**. Si un usuario posee $n$ juegos, el vector resultante $\vec{U}$ es la media aritmética de los vectores de todos sus juegos:

$$\vec{U} = \frac{1}{n} \sum_{i=1}^{n} \vec{G}_i$$

Este centroide representa el "punto de gravedad" de los gustos del usuario en el espacio vectorial.

## 4. Pipeline de Filtrado Estricto (Hard Constraints)

Para optimizar el rendimiento y garantizar la relevancia, el sistema aplica una máscara booleana previa al cálculo del coseno. Este proceso elimina el ruido (juegos sin reseñas o "shovelware") y respeta los límites físicos de la búsqueda:

1.  **Filtrado de Calidad:** Eliminación de registros donde $\text{Positive} + \text{Negative} = 0$.
2.  **Restricción de Rango:** $Año_{min} \leq Año_{juego} \leq Año_{max}$.
3.  **Restricción de Precio:** $Precio_{juego} \leq Precio_{max}$.
4.  **Reseña Mínima:** Conversión de categorías ordinales a escalares para asegurar que $Calidad_{juego} \geq Calidad_{solicitada}$.

## 5. Implementación Tecnológica

* **Backend:** FastAPI (Python 3.10+).
* **Procesamiento de Datos:** Pandas & NumPy.
* **Machine Learning:** Scikit-Learn (Cosine Similarity & MultiLabelBinarizer).
* **Integración:** Steamworks Web API para recuperación de bibliotecas en tiempo real.