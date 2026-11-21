import { PHASE_COLORS, phaseShortName } from '../simulation/labels.js'

const FINISHED = new Set(['done', 'error', 'skipped'])

// Cetiri faze kao "koraci": koja radi, koliko je zavrseno, klik bira fazu za prikaz toka.
export function Phases({ system, current, selected, phaseDone, status, feedback, onSelect }) {
  return (
    <section className="panel">
      <h2>Faze</h2>
      <div className="phases">
        {system.phases.map((p, i) => {
          const nodes = p.steps.flat()
          const finished = nodes.filter((n) => FINISHED.has(status[n.id])).length
          const cls = ['phase', current === p.id && 'active', phaseDone[p.id] && 'done', selected === p.id && 'selected']
            .filter(Boolean).join(' ')
          return (
            <button key={p.id} className={cls} style={{ '--pc': PHASE_COLORS[i % 4] }} onClick={() => onSelect(p.id)}>
              <div className="n">Faza {i + 1}</div>
              <div className="name">{phaseShortName(p.name)}</div>
              <div className="bar"><i style={{ width: `${nodes.length ? (100 * finished) / nodes.length : 0}%` }} /></div>
            </button>
          )
        })}
      </div>
      <div className="feedback">
        {feedback && (feedback.rework
          ? <>↺ <b>Povratna sprega:</b> vraćam se na fazu <b>{feedback.return_to}</b> (dorada {feedback.iteration})</>
          : <>Evaluacija završena: {feedback.reason || 'nema dorade.'}</>)}
      </div>
    </section>
  )
}
