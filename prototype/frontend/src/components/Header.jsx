import { useState } from 'react'

// Gornja traka: LLM rezim, status, brzina i pustanje snimaka ranijih pokretanja.
export function Header({ llmLabel, runStatus, speed, setSpeed, runs, onReplay }) {
  const [chosen, setChosen] = useState('')
  const prettyName = (f) =>
    f.replace(/^events_(\d{4})(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)\.json$/, '$3.$2.$1. $4:$5:$6')

  return (
    <header>
      <h1>Simulator nastavnog procesa</h1>
      <span className="badge">{llmLabel}</span>
      <span className="badge">{runStatus}</span>
      <span className="spacer" />
      <label className="badge">
        brzina{' '}
        <select value={speed} onChange={(e) => setSpeed(parseFloat(e.target.value))}>
          {[0.5, 1, 2, 5].map((v) => <option key={v} value={v}>{v}×</option>)}
        </select>
      </label>
      <select value={chosen} onChange={(e) => setChosen(e.target.value)}>
        <option value="">— snimak ranijeg pokretanja —</option>
        {runs.map((f) => <option key={f} value={f}>{prettyName(f)}</option>)}
      </select>
      <button className="ghost" onClick={() => onReplay(chosen)}>Pusti snimak</button>
    </header>
  )
}
