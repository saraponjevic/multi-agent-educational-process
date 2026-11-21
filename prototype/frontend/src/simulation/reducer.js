// REDUCER: (staro stanje, akcija) -> novo stanje.
// Svaki DOGADJAJ simulacije (engine/events.py na serveru) postaje akcija {type: 'event', ev}.
// Ovde nema crtanja ni cekanja - samo racunanje stanja; komponente ga posle nacrtaju.

import { ARTIFACT_TITLES, PHASE_COLORS } from './labels.js'

let msgId = 0
const msg = (kind, props) => ({ id: ++msgId, kind, ...props })

export function initialState() {
  return {
    system: null,          // faze, koraci, agenti, aktivnosti, ucenici (sa servera)
    started: false,        // dok ne stigne run_start, ostali dogadjaji se ignorisu
    topic: null,
    current: null,         // faza koja trenutno radi
    selected: null,        // faza prikazana u "Tok faze"
    iteration: 0,          // prolaz kroz povratnu spregu
    status: {},            // {id agenta/aktivnosti: 'running' | 'done' | 'error' | 'skipped'}
    phaseDone: {},
    rounds: {},            // {id faze: krug petlje}
    feedback: null,
    artifacts: [],         // najnoviji prvi
    messages: [msg('sys', { text: 'Zdravo! Napiši za koju temu želiš kurs, a ja ću pokrenuti agente: kurikulum → materijali → nastava → test i evaluacija. Sve što naprave pojaviće se desno.' })],
    students: {},          // {id: {learned, heard, scoreText}}
    total: 0,              // broj delova lekcije
    blackboard: null,      // deo lekcije koji nastavnik upravo predaje
    flights: [],           // tackice u letu (nastavnik -> ucenik)
    log: [],
  }
}

function freshStudents(system) {
  return Object.fromEntries((system?.students || []).map((s) => [s.id, { learned: 0, heard: 0, scoreText: '' }]))
}

function withSystem(state, system) {
  return { ...state, system, students: freshStudents(system), selected: system.phases[0]?.id }
}

// ----------------------------------------------------------------------
export function reducer(state, action) {
  switch (action.type) {
    case 'preview':                 // opis sistema pre pokretanja
      return withSystem(state, action.system)
    case 'reset':                   // novo pokretanje / snimak: cekamo run_start
      return { ...state, started: false }
    case 'say':
      return { ...state, messages: [...state.messages, msg(action.kind || 'sys', { text: action.text })] }
    case 'flight_done':
      return { ...state, flights: state.flights.filter((f) => f.key !== action.key) }
    case 'event':
      if (!state.started && action.ev.type !== 'run_start') return state
      return addLog(applyEvent(state, action.ev), action.ev)
    default:
      return state
  }
}

function addLog(state, ev) {
  const what = ev.agent || ev.activity || ev.student || ev.phase || ''
  const line = `${ev.seq}\t${ev.type}\t${what}${ev.status ? '\t' + ev.status : ''}${ev.absorbed != null ? '\tusvojio=' + ev.absorbed : ''}`
  return { ...state, log: [...state.log.slice(-400), line] }
}

function isArtifact(ev) {
  const out = ev.output
  if (ev.status !== 'ok' || !out || typeof out !== 'object') return false
  if (ev.agent === 'teacher') return !!out.done                    // samo kad preda sve delove
  if (ev.activity === 'learning') return false                     // ucenje se vidi u ucionici
  if (String(out.message || '').startsWith('Zdravo, ja sam')) return false   // hello world agent
  return Object.keys(out).some((k) => !k.startsWith('_') && !['message', 'received_from'].includes(k))
}

function makeArtifact(state, id, phase, output, iteration) {
  const i = state.system.phases.findIndex((p) => p.id === phase)
  return {
    key: `${id}-${iteration}-${state.artifacts.length}`,
    id, phase, output,
    title: ARTIFACT_TITLES[id] || id,
    color: PHASE_COLORS[(i < 0 ? 0 : i) % 4],
    version: (iteration || 0) + 1,
  }
}

// ----------------------------------------------------------------------
function applyEvent(s, ev) {
  switch (ev.type) {
    case 'run_start': {
      const fresh = withSystem({ ...initialState(), messages: s.messages, log: s.log }, ev.system)
      return {
        ...fresh, started: true, topic: ev.topic,
        messages: [...s.messages, msg('sys', { text: `Kurs: **${ev.topic}**`, note: ev.llm })],
      }
    }

    case 'phase_start': {
      const order = s.system.phases.map((p) => p.id)
      const idx = order.indexOf(ev.phase)
      const phaseDone = { ...s.phaseDone }
      order.slice(0, idx).forEach((p) => { phaseDone[p] = true })
      let { status, students, iteration } = s
      if (ev.iteration > iteration) {        // dorada: faze od ove pa nadalje krecu ispocetka
        iteration = ev.iteration
        status = { ...status }
        s.system.phases.slice(idx).forEach((p) => {
          phaseDone[p.id] = false
          p.steps.flat().forEach((n) => { delete status[n.id] })
        })
      }
      if (ev.phase === 'teaching') students = freshStudents(s.system)   // nova generacija ucenika
      const rounds = { ...s.rounds }
      delete rounds[ev.phase]
      return {
        ...s, phaseDone, status, students, iteration, rounds, current: ev.phase, selected: ev.phase,
        messages: [...s.messages, msg('phase', { text: `▶ ${ev.name}${ev.iteration ? ` (prolaz ${ev.iteration + 1})` : ''}` })],
      }
    }

    case 'agent_start':
    case 'activity_start': {
      const id = ev.agent || ev.activity
      const next = { ...s, status: { ...s.status, [id]: 'running' } }
      const phase = s.system.phases.find((p) => p.id === ev.phase)
      if (ev.round != null && phase?.loop) next.rounds = { ...s.rounds, [ev.phase]: ev.round }
      if (ev.activity === 'test_taking') next.students = mapStudents(s.students, () => ({ scoreText: '✎ piše test…' }))
      return next
    }

    case 'agent_end':
    case 'activity_end': {
      const id = ev.agent || ev.activity
      const next = { ...s, status: { ...s.status, [id]: ev.status === 'ok' ? 'done' : ev.status } }
      const messages = [...s.messages]
      if (ev.status === 'error') messages.push(msg('warn', { text: `⚠ **${id}**: ${ev.error}` }))

      const out = ev.output || {}
      if (ev.agent === 'teacher' && out.segment) {
        next.total = out.total || 0
        next.blackboard = { index: out.index, total: out.total, ...out.segment }
      }
      if (ev.agent === 'answer_grader' && out.grades) {
        next.students = mapStudents(s.students, (id) =>
          out.grades[id] ? { scoreText: `test: ${out.grades[id].score}/100` } : {})
      }
      if (ev.activity === 'test_taking') next.students = mapStudents(s.students, () => ({ scoreText: 'test predat, čeka ocenu' }))

      if (isArtifact(ev)) {
        const art = makeArtifact(s, id, ev.phase, out, ev.iteration)
        next.artifacts = [art, ...s.artifacts]
        messages.push(msg('artifact', { agent: id, artKey: art.key, title: art.title }))
      }
      next.messages = messages
      return next
    }

    case 'student_learned': {
      const st = s.students[ev.student]
      if (!st) return s
      return {
        ...s,
        students: { ...s.students, [ev.student]: { ...st, learned: ev.learned, heard: ev.heard } },
        flights: [...s.flights, { key: ev.seq, student: ev.student, absorbed: ev.absorbed }],
      }
    }

    case 'loop_round':
      return { ...s, rounds: { ...s.rounds, [ev.phase]: ev.round } }

    case 'feedback':
      return {
        ...s, feedback: ev,
        messages: ev.rework
          ? [...s.messages, msg('warn', { text: `↺ Evaluacija traži doradu → nazad na **${ev.return_to}**. ${ev.reason || ''}` })]
          : s.messages,
      }

    case 'run_end': {
      const phaseDone = Object.fromEntries(s.system.phases.map((p) => [p.id, true]))
      let artifacts = s.artifacts
      if (ev.files && Object.keys(ev.files).length) {
        const last = s.system.phases.at(-1).id
        artifacts = [makeArtifact(s, 'materijali', last, { files: ev.files }, s.iteration), ...artifacts]
      }
      const extra = ev.violations?.length ? ` Prekršena pravila u grafu znanja: ${ev.violations.length}.` : ''
      return {
        ...s, phaseDone, artifacts, current: null,
        messages: [...s.messages, msg('sys', { text: `✅ Gotovo! ${ev.summary || ''}${extra}` })],
      }
    }

    case 'run_error':
      return { ...s, messages: [...s.messages, msg('warn', { text: `⚠ Simulacija je pukla: ${ev.error}` })] }

    default:
      return s
  }
}

function mapStudents(students, change) {
  return Object.fromEntries(Object.entries(students).map(([id, st]) => [id, { ...st, ...change(id) }]))
}

// Koliko ms cekati posle dogadjaja, da bi animacija bila vidljiva (deli se sa brzinom).
export function delayFor(ev) {
  switch (ev.type) {
    case 'run_start': return 300
    case 'phase_start': return 500
    case 'agent_start':
    case 'activity_start': return 60
    case 'agent_end':
    case 'activity_end': return 140
    case 'student_learned': return 220
    case 'loop_round': return ev.done ? 200 : 120
    case 'feedback': return 600
    case 'run_end':
    case 'run_error': return 0
    default: return 30
  }
}
