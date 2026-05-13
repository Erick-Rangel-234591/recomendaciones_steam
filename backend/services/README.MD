# Steam Discovery Engine: Documentación Técnica y Fundamentos Matemáticos

Este proyecto implementa un sistema de recomendación híbrido basado en contenido que opera sobre un espacio vectorial de alta dimensionalidad. El motor procesa metadatos de más de 80,000 videojuegos para calcular afinidades semánticas mediante álgebra lineal y procesamiento matricial.

---

## 1. El Modelo Matemático: Similitud del Coseno en Espacios de Alta Dimensionalidad

El sistema no procesa "juegos" como entidades aisladas, sino como **tensores de características** situados en un espacio vectorial $n$-dimensional, donde cada dimensión representa un atributo único (Género o Tag) del catálogo de Steam.

### 1.1 Representación Vectorial y Espacio de Características
Cada juego $J$ se proyecta en un espacio vectorial $\mathbb{R}^n$. Inicialmente, los componentes son binarios (0 o 1), pero el motor los transforma mediante una ponderación escalar $W$. Un vector de juego $\mathbf{A}$ se define como:

$$\mathbf{A} = [a_1 w_1, a_2 w_2, \dots, a_n w_n]$$

Donde $a_i \in \{0, 1\}$ indica la presencia del atributo y $w_i$ es el peso asignado a esa dimensión según su importancia ontológica (Género: 0.45, Tag: 0.30, etc.).

### 1.2 Producto Escalar (Dot Product)
El numerador de la fórmula mide la coincidencia acumulada entre el perfil de búsqueda (o perfil de usuario) y cada juego del catálogo. Representa la suma de las proyecciones comunes:

$$\mathbf{A} \cdot \mathbf{B} = \sum_{i=1}^{n} a_i b_i$$

Si ambos vectores comparten una dimensión activa (ej. ambos son "RPG"), el producto suma el cuadrado de su peso a la magnitud total. Si uno de los dos carece del atributo ($0$), la dimensión se anula para ese cálculo, penalizando la falta de coincidencia estructural.

### 1.3 Normalización de Magnitud (Norma L2)
Para evitar el **sesgo de densidad** (donde juegos con muchas etiquetas parecen más similares solo por probabilidad), aplicamos la **Norma Euclídea**:

$$\|\mathbf{V}\| = \sqrt{\sum_{i=1}^{n} v_i^2}$$

Al dividir el producto escalar por el producto de las normas, el algoritmo realiza una **normalización de unidad**. Esto garantiza que el resultado dependa exclusivamente de la **orientación** del vector y no de la cantidad de etiquetas.

$$\text{similitud}(\mathbf{A}, \mathbf{B}) = \cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$

### 1.4 Interpretación del Ángulo $\theta$
* **$\theta = 0^\circ$ ($\cos \theta = 1$):** Vectores colineales. Coincidencia exacta.
* **$\theta = 90^\circ$ ($\cos \theta = 0$):** Vectores ortogonales. Sin intersección de gustos.
* **Match Score:** Traducimos el rango $[0.7, 1.0]$ en una escala porcentual del **70% al 100%**.

---

## 2. Arquitectura de Pesos (Ontología Ponderada)

Aplicamos una **Matriz de Pesos Estructurales** para priorizar la ontología sobre las etiquetas descriptivas:

| Dimensión | Peso ($W$) | Propósito Semántico |
| :--- | :--- | :--- |
| **Géneros** | **45%** | Estructura fundamental (ej. RPG, Action). |
| **Tags** | **30%** | Mecánicas secundarias (ej. Open World, Souls-like). |
| **Reseñas** | **15%** | Validación social y factor de calidad comunitaria. |
| **Precio** | **10%** | Accesibilidad económica relativa. |

---

## 3. Generación de Perfiles de Usuario

### A. Perfilado por Características (Vector Sintético)
El sistema crea un vector "ideal" basado en los filtros del frontend, activando dimensiones específicas con pesos predefinidos.

### B. Perfilado por Biblioteca (Centroide Geométrico)
Para recomendaciones basadas en Steam ID, calculamos el **Centroide de la Biblioteca**:

$$\vec{U}_{centroide} = \frac{\sum_{i=1}^{k} \vec{G}_i}{k}$$

Este vector promedio representa el "punto de gravedad" de los gustos del usuario en el espacio vectorial.

---

## 4. Pipeline de Filtrado Estricto (Hard Constraints)

Antes del cálculo vectorial, se aplica una máscara booleana para eliminar el ruido:
1.  **Limpieza de Datos:** Eliminación de juegos con 0 reseñas (Shovelware).
2.  **Rango Temporal:** $Año_{min} \leq Año_{juego} \leq Año_{max}$.
3.  **Límite de Costo:** $Precio_{juego} \leq Precio_{max}$.
4.  **Umbral de Calidad:** Conversión de categorías ordinales (`Very Positive`, etc.) a valores escalares para comparación de umbral.

---

## 5. Stack Tecnológico
* **Backend:** FastAPI (Python).
* **Ciencia de Datos:** Pandas, NumPy, Scikit-Learn.
* **API Externa:** Steamworks Web API.
* **Frontend:** React + Vite.