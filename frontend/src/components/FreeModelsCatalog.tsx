import { useEffect, useState } from 'react'
import { api } from '../api'
import type { FreeCatalogEntry } from '../types'
import { IconExternal, IconKey } from './Icon'

export default function FreeModelsCatalog({ onPick }: { onPick?: (provider: string, model: string) => void }) {
  const [catalog, setCatalog] = useState<FreeCatalogEntry[]>([])
  const [filter, setFilter] = useState<'all' | 'chat' | 'embedding'>('all')
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.freeModels().then((data) => {
      setCatalog(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <p className="muted">Cargando modelos gratuitos…</p>

  const filtered = catalog.map(entry => ({
    ...entry,
    models: entry.models.filter(m => {
      if (filter !== 'all' && m.type !== filter) return false
      if (q && !m.name.toLowerCase().includes(q.toLowerCase()) && !entry.label.toLowerCase().includes(q.toLowerCase())) return false
      return true
    })
  })).filter(e => e.models.length > 0)

  return (
    <div className="free-catalog">
      <div className="free-head">
        <h3>Modelos IA gratuitos para RAG</h3>
        <p className="muted">Elige un proveedor y genera tu API key — los gratuitos no requieren tarjeta en Groq, Google y OpenRouter.</p>
        <div className="toolbar" style={{marginTop: 12}}>
          <div className="chips">
            <button className={`chip ${filter==='all'?'on':''}`} onClick={()=>setFilter('all')}>Todos</button>
            <button className={`chip ${filter==='chat'?'on':''}`} onClick={()=>setFilter('chat')}>Chat (LLM)</button>
            <button className={`chip ${filter==='embedding'?'on':''}`} onClick={()=>setFilter('embedding')}>Embeddings</button>
          </div>
          <input placeholder="Buscar modelo…" value={q} onChange={e=>setQ(e.target.value)} style={{maxWidth: 200}} />
        </div>
      </div>

      {filtered.map(entry => (
        <div key={entry.provider} className="free-group">
          <div className="free-group-head">
            <div>
              <strong>{entry.label}</strong> <span className="muted" style={{fontSize:'0.75rem'}}>· {entry.free_note}</span>
            </div>
            <div className="free-links">
              <a href={entry.key_url} target="_blank" rel="noreferrer" className="free-link"><IconKey size={13} /> Crear API key <IconExternal size={11} /></a>
              {entry.docs_url && <a href={entry.docs_url} target="_blank" rel="noreferrer" className="free-link muted">Docs <IconExternal size={11} /></a>}
            </div>
          </div>
          <div className="free-models">
            {entry.models.map(m => (
              <div key={m.name} className={`free-model ${m.free?'free':''}`}>
                <div className="free-model-top">
                  <code>{m.name}</code>
                  <span className={`badge badge-${m.type}`}>{m.type}</span>
                  {m.free && <span className="badge" style={{color:'#34d399', borderColor:'#34d399'}}>gratis</span>}
                </div>
                <p className="muted" style={{fontSize:'0.75rem', margin:'4px 0 8px'}}>{m.desc}</p>
                {onPick && (
                  <button className="ghost" style={{fontSize:'0.75rem', padding:'4px 10px'}} onClick={()=>onPick(entry.provider, m.name)}>
                    Usar este modelo
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      <div className="free-foot muted" style={{marginTop: 16, fontSize:'0.78rem'}}>
        <p>Consejo: empieza con <strong>Google gemini-2.0-flash</strong> (gratis, 1M contexto) + <strong>Groq llama-3.3-70b-versatile</strong> como respaldo. Para embeddings usa <code>text-embedding-004</code> (Google, gratis) o <code>nomic-embed-text</code> local con Ollama.</p>
        <p>Para Ollama instala <a href="https://ollama.com/download" target="_blank" rel="noreferrer">ollama.com/download</a> y ejecuta <code>ollama pull llama3.2 &amp;&amp; ollama pull nomic-embed-text</code> — no necesitas clave.</p>
      </div>
    </div>
  )
}
