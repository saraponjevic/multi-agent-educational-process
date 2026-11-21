import { useEffect, useRef } from 'react'
import { studentLabel } from '../simulation/labels.js'

// UCIONICA (SVG): nastavnik levo, ucenici desno.
// Kad nastavnik isporuci deo lekcije, ka svakom uceniku poleti tackica:
//   zelena stigne do ucenika = usvojio,  posivi i padne = cuo, ali nije usvojio.

const TEACHER = { x: 110, y: 140, r: 36 }
const STUDENT_X = 430
const BAR_W = 150

function studentY(i, n) {
  return n === 1 ? 140 : 40 + i * (200 / (n - 1))
}

// Jedna tackica u letu - animira se preko Web Animations API, pa javi da je gotova.
function Dot({ flight, target, speed, onDone }) {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    const dx = target.x - (TEACHER.x + TEACHER.r)
    const dy = target.y - TEACHER.y
    const frames = flight.absorbed
      ? [{ transform: 'translate(0px, 0px)' }, { transform: `translate(${dx}px, ${dy}px)` }]
      : [
          { transform: 'translate(0px, 0px)', fill: 'var(--absorb)', opacity: 1 },
          { transform: `translate(${dx * 0.6}px, ${dy * 0.6}px)`, fill: 'var(--miss)', opacity: 1, offset: 0.6 },
          { transform: `translate(${dx * 0.8}px, ${dy * 0.8 + 40}px)`, fill: 'var(--miss)', opacity: 0 },
        ]
    const duration = 650 / speed
    const anim = el.animate(frames, { duration, easing: 'ease-in-out', fill: 'forwards' })
    const safety = setTimeout(() => onDone(flight.key), duration + 400)   // ako tab nije vidljiv
    anim.onfinish = () => onDone(flight.key)
    return () => { clearTimeout(safety); anim.cancel() }
  }, [flight, target.x, target.y, speed, onDone])

  return <circle ref={ref} cx={TEACHER.x + TEACHER.r} cy={TEACHER.y} r={7} style={{ fill: 'var(--absorb)' }} />
}

export function Classroom({ system, students, total, blackboard, flights, speed, onFlightDone }) {
  const ids = Object.keys(students)
  const pos = Object.fromEntries(ids.map((id, i) => [id, { x: STUDENT_X - 28, y: studentY(i, ids.length) }]))

  return (
    <section className="panel">
      <h2>Učionica (faza 3: nastavnik isporučuje delove lekcije · faza 4: test)</h2>
      <div className="blackboard">
        {blackboard ? (
          <>
            <span className="small">Deo {blackboard.index + 1} od {blackboard.total} · jedinica {blackboard.unit}</span><br />
            <b>{blackboard.concept}</b> — {String(blackboard.content).slice(0, 220)}
            {String(blackboard.content).length > 220 && '…'}
          </>
        ) : (
          <span className="small">Tabla je prazna — čas još nije počeo.</span>
        )}
      </div>

      <svg className="room" viewBox="0 0 640 280" role="img" aria-label="Nastavnik šalje delove lekcije učenicima">
        <circle cx={TEACHER.x} cy={TEACHER.y} r={TEACHER.r} style={{ fill: 'var(--p3)' }} />
        <text x={TEACHER.x} y={TEACHER.y + 5} textAnchor="middle" className="on-color">Nastavnik</text>

        {ids.map((id, i) => {
          const st = students[id]
          const y = studentY(i, ids.length)
          const denom = Math.max(total, st.heard, 1)
          return (
            <g key={id}>
              <line x1={TEACHER.x + TEACHER.r} y1={TEACHER.y} x2={STUDENT_X - 26} y2={y} className="wire" />
              <circle cx={STUDENT_X} cy={y} r={26} style={{ fill: 'var(--accent)' }} opacity={0.85} />
              <text x={STUDENT_X} y={y + 4} textAnchor="middle" className="on-color small">{studentLabel(system, id)}</text>
              <rect x={470} y={y - 12} width={BAR_W} height={10} rx={5} className="track" />
              <rect x={470} y={y - 12} width={(BAR_W * st.learned) / denom} height={10} rx={5}
                    style={{ fill: 'var(--absorb)', transition: 'width .4s' }} />
              <text x={470} y={y + 12} className="muted-text">
                usvojio {st.learned} / čuo {st.heard}{total ? ` / ukupno ${total}` : ''}
              </text>
              <text x={470} y={y + 26} className="score-text">{st.scoreText}</text>
            </g>
          )
        })}

        {flights.map((f) => pos[f.student] && (
          <Dot key={f.key} flight={f} target={pos[f.student]} speed={speed} onDone={onFlightDone} />
        ))}
      </svg>

      <div className="legend">
        <span><i className="dot" style={{ background: 'var(--absorb)' }} />deo lekcije usvojen</span>
        <span><i className="dot" style={{ background: 'var(--miss)' }} />čuo, ali nije usvojio</span>
      </div>
    </section>
  )
}
