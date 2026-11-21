import { Fragment } from 'react'
import { studentLabel } from '../simulation/labels.js'

// "Tok faze": koraci jedne faze, agenti (puna ivica) i aktivnosti (isprekidana),
// a koraci koji su u PETLJI su u narandzastom okviru sa brojem kruga.
export function PhaseBoard({ system, selected, status, rounds, total, artifactIds, onOpenAgent }) {
  const phase = system.phases.find((p) => p.id === selected) || system.phases[0]
  const loop = phase.loop

  const node = (n) => {
    const clickable = artifactIds.has(n.id)
    return (
      <div key={n.id} title={n.name}
           className={`node ${n.kind} ${status[n.id] || 'idle'}${clickable ? ' has-art' : ''}`}
           onClick={clickable ? () => onOpenAgent(n.id) : undefined}>
        <div className="kind">{n.kind === 'activity' ? 'aktivnost' : 'agent'}</div>
        <div className="id">{n.id}</div>
        {n.kind === 'activity' && (
          <>
            <div className="chips">
              {n.participants.map((p) => <span key={p} className="chip">{studentLabel(system, p)}</span>)}
            </div>
            <div className="kind">nad: {n.resource || '-'}</div>
          </>
        )}
      </div>
    )
  }

  const stepColumn = (step) => (
    <div className="step" key={step[0].step}>
      <div className="h">korak {step[0].step}{step.length > 1 ? ' · paralelno' : ''}</div>
      {step.map(node)}
    </div>
  )

  // grupisanje: koraci u petlji idu u jedan okvir
  const parts = []
  for (let i = 0; i < phase.steps.length; ) {
    const num = phase.steps[i][0].step
    if (loop && num === loop.from_step) {
      const group = []
      while (i < phase.steps.length && phase.steps[i][0].step <= loop.to_step) group.push(phase.steps[i++])
      const r = rounds[phase.id]
      parts.push(
        <div className="loopgroup" key={`loop-${num}`}>
          <span className="lbl">
            ↺ petlja dok ne važi {loop.until}{r != null && ` · krug ${r + 1}${total ? '/' + total : ''}`}
          </span>
          {group.map((s, k) => <Fragment key={k}>{k > 0 && <span className="arrow">→</span>}{stepColumn(s)}</Fragment>)}
        </div>,
      )
    } else {
      parts.push(stepColumn(phase.steps[i++]))
    }
  }

  return (
    <section className="panel">
      <h2>Tok faze: {phase.name}</h2>
      <div className="board">
        {parts.map((p, k) => <Fragment key={k}>{k > 0 && <span className="arrow">→</span>}{p}</Fragment>)}
      </div>
      <div className="legend">
        <span><i className="dot" style={{ background: 'var(--run)' }} />radi</span>
        <span><i className="dot" style={{ background: 'var(--ok)' }} />završio</span>
        <span><i className="dot" style={{ background: 'var(--err)' }} />greška</span>
        <span>puna ivica = agent · isprekidana = aktivnost (nije agent) · klik na završenog agenta otvara njegov artefakt</span>
      </div>
    </section>
  )
}
