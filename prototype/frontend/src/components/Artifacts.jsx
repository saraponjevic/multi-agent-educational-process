import { useEffect, useState } from 'react'
import { phaseShortName } from '../simulation/labels.js'
import { Markdown, ValueView } from './Content.jsx'

// Desno: sve sto su agenti napravili (najnovije gore). Klik otvara sadrzaj.
export function Artifacts({ system, artifacts, onOpen }) {
  return (
    <section className="panel">
      <h2>Artefakti (šta su agenti napravili)</h2>
      <div className="artifacts">
        {!artifacts.length && <span className="empty">Još ništa.</span>}
        {artifacts.map((a) => {
          const phase = system.phases.find((p) => p.id === a.phase)
          return (
            <button key={a.key} className="art" style={{ '--pc': a.color }} onClick={() => onOpen(a)}>
              <div className="title">
                {a.title}
                {a.version > 1 && <span className="badge">verzija {a.version}</span>}
              </div>
              <div className="meta">{phase ? phaseShortName(phase.name) : a.phase} · {a.id}</div>
            </button>
          )
        })}
      </div>
    </section>
  )
}

// Prozor sa sadrzajem artefakta: fajlovi (markdown) u tabovima, ostalo kao citljiv JSON.
export function ArtifactModal({ artifact, onClose }) {
  const files = artifact?.output?.files && typeof artifact.output.files === 'object'
    ? Object.keys(artifact.output.files) : []
  const [tab, setTab] = useState(files[0])

  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  if (!artifact) return null
  const current = files.includes(tab) ? tab : files[0]

  return (
    <div className="backdrop" onClick={onClose}>
      <div className="modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>{artifact.title} — {artifact.id}{artifact.version > 1 && ` (verzija ${artifact.version})`}</h3>
          <button className="ghost" onClick={onClose}>Zatvori</button>
        </div>
        <div className="modal-body">
          {files.length ? (
            <>
              <div className="tabs">
                {files.map((f) => (
                  <button key={f} className={f === current ? '' : 'ghost'} onClick={() => setTab(f)}>{f}</button>
                ))}
              </div>
              <Markdown text={artifact.output.files[current]} />
            </>
          ) : (
            <ValueView value={artifact.output} />
          )}
        </div>
      </div>
    </div>
  )
}

export function EventLog({ lines }) {
  return (
    <details className="log">
      <summary>Dnevnik događaja (sirovo)</summary>
      <pre>{lines.join('\n')}</pre>
    </details>
  )
}
