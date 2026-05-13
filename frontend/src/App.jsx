import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [modo, setModo] = useState('biblioteca'); 
  const [steamId, setSteamId] = useState('');
  
  // Estado inicial con TODOS los parámetros requeridos por el backend
  const [filtros, setFiltros] = useState({
    generos_deseados: [],
    tags_deseados: [],
    precio_maximo: 60,
    anio_lanzamiento_min: 2010,
    anio_lanzamiento_max: 2026,
    resena_minima: "Positive",
    solo_gratuitos: false
  });

  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableGenres, setAvailableGenres] = useState([]);
  const [availableTags, setAvailableTags] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const openGameDetails = (juego) => {
    setSelectedGame(juego);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedGame(null);
  };

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [genresRes, tagsRes] = await Promise.all([
          fetch('http://localhost:8000/api/catalog/genres'),
          fetch('http://localhost:8000/api/catalog/tags')
        ]);
        const genresData = await genresRes.json();
        const tagsData = await tagsRes.json();
        setAvailableGenres(genresData.genres);
        setAvailableTags(tagsData.tags);
      } catch (err) {
        console.error('Error fetching options:', err);
      }
    };
    fetchOptions();
  }, []);

  const ejecutarBusqueda = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let url = 'http://localhost:8000/api/recomendaciones/';
      let opciones = {};

      if (modo === 'biblioteca') {
        url += `biblioteca/${steamId}`;
        opciones = { method: 'GET' };
      } else {
        url += 'caracteristicas';
        opciones = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(filtros)
        };
      }

      const response = await fetch(url, opciones);
      const data = await response.json();
      
      if (!response.ok) throw new Error(data.detail || 'Error en la petición');
      setResultados(data.recomendaciones);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="steam-app">
      <header className="hero-section">
        <h1 className="title-gradient">Steam Discovery Engine</h1>
        <p className="subtitle">Algoritmo de Similitud del Coseno basado en Ontología de Videojuegos</p>
      </header>

      <div className="control-panel">
        <div className="tab-container">
          <button className={`tab ${modo === 'biblioteca' ? 'active' : ''}`} onClick={() => setModo('biblioteca')}>
            <i className="fas fa-user-circle"></i> Mi Biblioteca
          </button>
          <button className={`tab ${modo === 'filtros' ? 'active' : ''}`} onClick={() => setModo('filtros')}>
            <i className="fas fa-sliders-h"></i> Filtros Avanzados
          </button>
        </div>

        <form onSubmit={ejecutarBusqueda} className="search-form">
          {modo === 'biblioteca' ? (
            <div className="input-single">
              <label>Steam ID de Usuario</label>
              <input 
                type="text" 
                placeholder="Ej: 76561198..." 
                value={steamId}
                onChange={(e) => setSteamId(e.target.value)}
                className="main-input"
              />
            </div>
          ) : (
            <div className="advanced-filters-grid">
              {/* FILA 1: Ontología (Géneros y Tags) */}
              <div className="filter-item full-width">
                <label>Géneros Deseados</label>
                <select multiple value={filtros.generos_deseados} 
                  onChange={(e) => setFiltros({...filtros, generos_deseados: Array.from(e.target.selectedOptions, option => option.value)})}>
                  {availableGenres.map(genre => (
                    <option key={genre} value={genre}>{genre}</option>
                  ))}
                </select>
              </div>
              <div className="filter-item full-width">
                <label>Etiquetas (Tags) Específicas</label>
                <select multiple value={filtros.tags_deseados} 
                  onChange={(e) => setFiltros({...filtros, tags_deseados: Array.from(e.target.selectedOptions, option => option.value)})}>
                  {availableTags.map(tag => (
                    <option key={tag} value={tag}>{tag}</option>
                  ))}
                </select>
              </div>

              {/* FILA 2: Precio y Tipo */}
              <div className="filter-item">
                <label>Precio Máximo ($)</label>
                <input type="number" value={filtros.precio_maximo} 
                  onChange={(e) => setFiltros({...filtros, precio_maximo: parseFloat(e.target.value)})} />
              </div>
              <div className="filter-item checkbox-item">
                <label>Solo Gratuitos</label>
                <input type="checkbox" checked={filtros.solo_gratuitos} 
                  onChange={(e) => setFiltros({...filtros, solo_gratuitos: e.target.checked})} />
              </div>

              {/* FILA 3: Fechas y Reseñas */}
              <div className="filter-item">
                <label>Año Mínimo</label>
                <input type="number" value={filtros.anio_lanzamiento_min} 
                  onChange={(e) => setFiltros({...filtros, anio_lanzamiento_min: parseInt(e.target.value)})} />
              </div>
              <div className="filter-item">
                <label>Año Máximo</label>
                <input type="number" value={filtros.anio_lanzamiento_max} 
                  onChange={(e) => setFiltros({...filtros, anio_lanzamiento_max: parseInt(e.target.value)})} />
              </div>
              <div className="filter-item">
                <label>Reseña Mínima</label>
                <select value={filtros.resena_minima} onChange={(e) => setFiltros({...filtros, resena_minima: e.target.value})}>
                  <option value="Overwhelmingly Positive">Extremadamente Positivas</option>
                  <option value="Very Positive">Muy Positivas</option>
                  <option value="Positive">Positivas</option>
                  <option value="Mostly Positive">Mayormente Positivas</option>
                  <option value="Mixed">Mixtas</option>
                  <option value="Mostly Negative">Mayormente Negativas</option>
                  <option value="Negative">Negativas</option>
                  <option value="Very Negative">Muy Negativas</option>
                  <option value="Overwhelmingly Negative">Extremadamente Negativas</option>
                </select>
              </div>
            </div>
          )}

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? <span className="loader"></span> : 'Generar Recomendaciones'}
          </button>
        </form>
      </div>

      {error && <div className="alert-error">{error}</div>}

      <main className="results-container">
        <div className="grid">
          {resultados.map((juego) => (
            <article key={juego.app_id} className="game-card" onClick={() => openGameDetails(juego)}>
              <div className="card-image">
                <img src={juego.imagen_url} alt={juego.titulo} />
                <div className="score-badge">{(juego.match_score).toFixed(1)}% Match</div>
              </div>
              <div className="card-body">
                <h3>{juego.titulo}</h3>
                <div className="tags">
                  {juego.generos.slice(0, 2).map(g => <span key={g} className="tag-genre">{g}</span>)}
                </div>
                <div className="card-footer">
                  <span className="price">{juego.precio === 0 ? 'Free' : `$${juego.precio}`}</span>
                  <span className="review">{juego.resena}</span>
                </div>
              </div>
            </article>
          ))}
        </div>
      </main>

      {showModal && selectedGame && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>×</button>
            <div className="modal-header">
              <img src={selectedGame.imagen_url} alt={selectedGame.titulo} className="modal-image" />
              <div className="modal-title-section">
                <h2>{selectedGame.titulo}</h2>
                <div className="modal-match-score">
                  <span className="match-percentage">{selectedGame.match_score.toFixed(1)}% Match</span>
                  <span className="match-explanation">
                    Este juego fue recomendado porque coincide con tus preferencias
                  </span>
                </div>
              </div>
            </div>
            <div className="modal-details">
              <div className="detail-section">
                <h3>Características del Juego</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <strong>Precio:</strong> {selectedGame.precio === 0 ? 'Gratuito' : `$${selectedGame.precio}`}
                  </div>
                  <div className="detail-item">
                    <strong>Fecha de Lanzamiento:</strong> {new Date(selectedGame.fecha_lanzamiento).toLocaleDateString()}
                  </div>
                  <div className="detail-item">
                    <strong>Reseñas:</strong> {selectedGame.resena}
                  </div>
                  <div className="detail-item">
                    <strong>Tipo:</strong> {selectedGame.es_gratuito ? 'Gratuito' : 'Pago'}
                  </div>
                </div>
              </div>
              <div className="detail-section">
                <h3>Géneros</h3>
                <div className="tags-list">
                  {selectedGame.generos.map(g => (
                    <span key={g} className="tag-genre">{g}</span>
                  ))}
                </div>
              </div>
              <div className="detail-section">
                <h3>Etiquetas (Tags)</h3>
                <div className="tags-list">
                  {selectedGame.tags.map(t => (
                    <span key={t} className="tag">{t}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App