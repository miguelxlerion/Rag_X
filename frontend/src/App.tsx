import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import type { Agent, AgentType } from './types'
import AgentCard from './components/AgentCard'
import AgentForm from './components/AgentForm'
import PlatformConfigForm from './components/PlatformConfigForm'
import FreeModelsCatalog from './components/FreeModelsCatalog'
import ConfigBackup from './components/ConfigBackup'
import ChatQuery from './components/ChatQuery'
import DocumentsList from './components/DocumentsList'
import ChatDocuments from './components/ChatDocuments'
import { IconBeaker } from './components/Icon'

type Tab = 'agents' | 'free' | 'search' | 'chat' | 'documents' | 'docs_chat'

const TABS: { key: Tab; label: string }[] = [
  { key: 'agents', label: 'Agentes IA' },
  { key: 'free', label: 'Modelos Gratis' },
  { key: 'search', label: 'Búsqueda' },
  { key: 'chat', label: 'Chat' },
  { key: 'documents', label: 'Documentos' },
  { key: 'docs_chat', label: 'Chat y documentos' }
]

const FILTERS: { key: AgentType | 'all'; label: string }[] = [
  { key: 'all', label: 'Todos' },
  { key: 'chat', label: 'Generación' },
  { key: 'embedding', label: 'Embeddings' },
  { key: 'reranker', label: 'Re-ranking' }
]

export default function App() {
  const [tab, setTab] = useState<Tab>('agents')
  const [agents, setAgents] = useState<Agent[]>([])
  const [filter, setFilter] = useState<AgentType | 'all'>('all')
  const [editing, setEditing] = useState<Agent | null | undefined>(undefined)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setAgents(await api.agents())
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const visible = filter === 'all' ? agents : agents.filter((a) => a.agent_type === filter)

  return (
    <div className="admin">
      <header className="top">
        <h1>Panel de Administración · RAG</h1>
        <nav className="tabs">
          {TABS.map((t) => (
            <button key={t.key} className={tab === t.key ? 'on' : ''} onClick={() => setTab(t.key)}>
              {t.label}
            </button>
          ))}
        </nav>
        <nav className="jumps">
          <a href="http://localhost:5555" target="_blank" rel="noreferrer" title="Flower — monitor Celery (admin / admin123)">Monitor Colas</a>
          <a href="http://localhost:8000/api/metrics" target="_blank" rel="noreferrer" title="Métricas Prometheus del RAG">Métricas API</a>
        </nav>
      </header>

      {tab === 'agents' ? (
        <main className="agents">
          <div className="toolbar">
            <div className="chips">
              {FILTERS.map((f) => (
                <button key={f.key} className={`chip ${filter === f.key ? 'on' : ''}`} onClick={() => setFilter(f.key)}>
                  {f.label}
                </button>
              ))}
            </div>
            <div style={{display:'flex', gap:8}}>
              <button className="ghost" onClick={async () => {
                if (!confirm('¿Crear 9 agentes de prueba gratuitos? (no duplica existentes)')) return
                try {
                  const res = await fetch('/api/agents/seed-test-agents/', {method:'POST'})
                  if (!res.ok) throw new Error(await res.text())
                  load()
                } catch(e){
                  alert((e as Error).message + ' — Ejecuta: docker compose exec web python manage.py seed_test_agents')
                }
              }} style={{display:'inline-flex', alignItems:'center', gap:6}}><IconBeaker size={14} /> Crear agentes prueba</button>
              <button className="primary" onClick={() => setEditing(null)}>+ Nuevo agente</button>
            </div>
          </div>
          {error && <p className="err banner">No se pudo cargar: {error}</p>}
          {loading ? (
            <p className="muted">Cargando agentes…</p>
          ) : visible.length === 0 ? (
            <p className="muted">No hay agentes de este tipo. Crea el primero o genera los de prueba.</p>
          ) : (
            <div className="grid">
              {visible.map((a) => (
                <AgentCard key={a.id} agent={a} onChanged={load} onEdit={setEditing} />
              ))}
            </div>
          )}
          <div style={{marginTop:24}}>
            <ConfigBackup onRestored={load} />
          </div>
        </main>
      ) : tab === 'free' ? (
        <main className="agents">
          <FreeModelsCatalog onPick={(provider, model) => {
            const type = model.includes('embed') || model.includes('bge') || model.includes('nomic') ? 'embedding' as const : 'chat' as const
            setEditing({ id: 0, name: `${provider} ${model}`, agent_type: type, provider: provider as any, model, description: 'Creado desde catálogo gratis', temperature: 0.2, max_tokens: 1024, top_k: 5, system_prompt: '', embedding_dim: model.includes('768') ? 768 : 1536, has_api_key: false, api_key_masked: '', is_active: false, is_fallback: false, fallback_order: 0, created_at:'', updated_at:'', agent_type_display:'' } as any)
          }} />
        </main>
      ) : tab === 'search' ? (
        <main className="agents">
          <PlatformConfigForm />
        </main>
      ) : tab === 'chat' ? (
        <main className="agents">
          <ChatQuery />
        </main>
      ) : tab === 'documents' ? (
        <main className="agents">
          <DocumentsList />
        </main>
      ) : (
        <main className="agents">
          <ChatDocuments />
        </main>
      )}

      {editing !== undefined && (
        <AgentForm agent={editing} onClose={() => setEditing(undefined)} onSaved={() => { setEditing(undefined); load() }} />
      )}
    </div>
  )
}
