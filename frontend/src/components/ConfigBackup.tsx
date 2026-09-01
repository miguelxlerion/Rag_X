import { useState } from 'react'
import { api } from '../api'
import { IconDownload, IconSave, IconUpload } from './Icon'

const STORAGE_KEY = 'rag_admin_backup_hint'

export default function ConfigBackup({ onRestored }: { onRestored?: () => void }) {
  const [msg, setMsg] = useState<string|null>(null)

  async function exportConfig() {
    try {
      const [agents, platform] = await Promise.all([api.agents(), api.platformConfig()])
      const payload = {
        exported_at: new Date().toISOString(),
        agents: agents.map(a => ({
          name: a.name,
          agent_type: a.agent_type,
          provider: a.provider,
          model: a.model,
          base_url: a.base_url,
          description: a.description,
          temperature: a.temperature,
          max_tokens: a.max_tokens,
          top_k: a.top_k,
          system_prompt: a.system_prompt,
          embedding_dim: a.embedding_dim,
          is_active: a.is_active,
          is_fallback: a.is_fallback,
          fallback_order: a.fallback_order
        })),
        platform,
        note: 'API keys no se exportan por seguridad — reintroduce cada clave al importar. Guarda este JSON en local.'
      }
      const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'})
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `rag-config-${new Date().toISOString().slice(0,10)}.json`
      a.click()
      URL.revokeObjectURL(url)
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ exported_at: payload.exported_at, count: agents.length }))
      setMsg(`Configuración exportada: ${agents.length} agentes + plataforma. Guardado en Downloads.`)
    } catch (e) {
      setMsg((e as Error).message)
    }
  }

  async function importConfig(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const text = await file.text()
      const data = JSON.parse(text)
      if (data.platform) {
        await api.savePlatformConfig(data.platform)
      }
      if (Array.isArray(data.agents)) {
        for (const ag of data.agents) {
          try {
            await api.createAgent(ag)
          } catch (err) {
            // si ya existe, intenta actualizar por nombre
            const existing = (await api.agents()).find(a => a.name === ag.name)
            if (existing) await api.updateAgent(existing.id, ag)
            else throw err
          }
        }
      }
      setMsg(`Importado: ${data.agents?.length ?? 0} agentes. Revisa y añade las API keys — no se importan por seguridad.`)
      onRestored?.()
    } catch (err) {
      setMsg((err as Error).message)
    }
    e.target.value = ''
  }

  function saveLocalHint() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ saved_at: new Date().toISOString(), hint: 'Usa Exportar para guardar JSON completo' }))
    setMsg('Preferencia guardada en localStorage (este navegador). Usa Exportar para backup completo.')
  }

  const hint = (() => {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') } catch { return null }
  })()

  return (
    <div className="cfg">
      <h4>Guardar configuración (local)</h4>
      <p className="muted">Todo queda en la base de datos (Postgres) y persiste tras reiniciar Docker. Usa estas herramientas para no re-escribir claves.</p>
      <div className="cfg-actions">
        <button onClick={exportConfig} style={{display:'inline-flex', alignItems:'center', gap:6}}><IconDownload size={14} /> Exportar JSON</button>
        <label className="ghost" style={{padding:'8px 14px', border:'1px solid var(--border)', borderRadius:8, cursor:'pointer', fontSize:'0.82rem', display:'inline-flex', alignItems:'center', gap:6}}>
          <IconUpload size={14} /> Importar JSON
          <input type="file" accept=".json" onChange={importConfig} style={{display:'none'}} />
        </label>
        <button className="ghost" onClick={saveLocalHint} style={{display:'inline-flex', alignItems:'center', gap:6}}><IconSave size={14} /> Guardar en este navegador</button>
      </div>
      {hint && <p className="muted" style={{fontSize:'0.72rem'}}>Último backup: {hint.exported_at || hint.saved_at} · {hint.count ? `${hint.count} agentes` : ''}</p>}
      {msg && <p className={msg.includes('Exportado')||msg.includes('Importado')||msg.includes('Guardado') ? 'ok' : 'err'}>{msg}</p>}
      <p className="muted" style={{fontSize:'0.72rem', marginTop:8}}>
        Nota de seguridad: las <strong>API keys no se incluyen</strong> en el JSON — se guardan cifradas (Fernet) en el backend. Al importar, reintroduce cada clave y pulsa <em>Probar API</em> antes de activar.
      </p>
    </div>
  )
}
