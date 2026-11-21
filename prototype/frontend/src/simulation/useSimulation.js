// HOOK useSimulation - sve sto stranica radi sa simulacijom:
//   - start(topic):  pokreni novu simulaciju i prati je UZIVO (pita server svakih 500 ms)
//   - replay(name):  pusti SNIMAK ranijeg pokretanja
//   - red cekanja:   dogadjaji se ne crtaju svi odjednom, nego jedan po jedan sa malom pauzom
//                    (delayFor), da bi se videlo kretanje kroz faze i tackice u ucionici

import { useCallback, useEffect, useReducer, useRef, useState } from 'react'
import { api } from '../api.js'
import { delayFor, initialState, reducer } from './reducer.js'

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

export function useSimulation() {
  const [state, dispatch] = useReducer(reducer, undefined, initialState)
  const [runStatus, setRunStatus] = useState('spremno')
  const [llmLabel, setLlmLabel] = useState('…')
  const [runs, setRuns] = useState([])
  const [speed, setSpeedState] = useState(1)

  const speedRef = useRef(1)
  const queue = useRef([])
  const playing = useRef(false)
  const playId = useRef(0)
  const poll = useRef({ timer: null, lastSeq: 0, startedAt: 0 })

  const setSpeed = useCallback((v) => { speedRef.current = v; setSpeedState(v) }, [])

  // ---------------- red cekanja ----------------
  const pump = useCallback(async () => {
    playing.current = true
    const my = playId.current
    while (queue.current.length && my === playId.current) {
      const ev = queue.current.shift()
      dispatch({ type: 'event', ev })
      if (ev.type === 'run_end') setRunStatus('završeno')
      if (ev.type === 'run_error') setRunStatus('greška')
      const d = delayFor(ev)
      if (d) await sleep(d / speedRef.current)
    }
    if (my === playId.current) playing.current = false
  }, [])

  const enqueue = useCallback((evts) => {
    queue.current.push(...evts)
    if (!playing.current) pump()
  }, [pump])

  const stopPlayback = useCallback(() => {
    playId.current++
    queue.current = []
    playing.current = false
  }, [])

  const loadRuns = useCallback(async () => {
    try { setRuns((await api.runs()).runs) } catch { /* server nije dostupan */ }
  }, [])

  // ---------------- uzivo ----------------
  const stopPolling = useCallback(() => {
    clearInterval(poll.current.timer)
    poll.current.timer = null
  }, [])

  const tick = useCallback(async () => {
    const p = poll.current
    try {
      const r = await api.events(p.lastSeq)
      // server je poceo novu simulaciju (lista dogadjaja resetovana) -> citamo od pocetka
      if (r.total < p.lastSeq) { p.lastSeq = 0; return }
      if (r.events.length) p.lastSeq = r.events.at(-1).seq + 1
      enqueue(r.events.filter((e) => e.time >= p.startedAt - 2))
      if (!r.running && !r.events.length) {
        stopPolling()
        if (r.error) dispatch({ type: 'say', kind: 'warn', text: `⚠ ${r.error}` })
        loadRuns()
      }
    } catch (e) {
      console.error(e)
    }
  }, [enqueue, loadRuns, stopPolling])

  const startPolling = useCallback((startedAt) => {
    stopPolling()
    poll.current = { timer: setInterval(tick, 500), lastSeq: 0, startedAt }
    setRunStatus('radi…')
  }, [stopPolling, tick])

  // ---------------- akcije za komponente ----------------
  const start = useCallback(async (topic) => {
    stopPlayback()
    dispatch({ type: 'reset' })
    dispatch({ type: 'say', kind: 'user', text: `Želim kurs o: ${topic}` })
    try {
      await api.start(topic)
      startPolling(Date.now() / 1000)
    } catch (e) {
      dispatch({ type: 'say', kind: 'warn', text: `⚠ ${e.message}` })
    }
  }, [startPolling, stopPlayback])

  const replay = useCallback(async (name) => {
    if (!name) {
      dispatch({ type: 'say', kind: 'warn', text: 'Izaberi snimak iz liste gore desno.' })
      return
    }
    stopPolling()
    stopPlayback()
    dispatch({ type: 'reset' })
    dispatch({ type: 'say', kind: 'user', text: `▶ Puštam snimak ${name}` })
    setRunStatus('snimak')
    try {
      enqueue((await api.replay(name)).events || [])
    } catch (e) {
      dispatch({ type: 'say', kind: 'warn', text: `⚠ ${e.message}` })
    }
  }, [enqueue, stopPlayback, stopPolling])

  const flightDone = useCallback((key) => dispatch({ type: 'flight_done', key }), [])

  // ---------------- pocetak: opis sistema, snimci, parametri iz adrese ----------------
  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const r = await api.system()
        if (cancelled) return
        dispatch({ type: 'preview', system: r.system })
        setLlmLabel(r.llm_enabled ? r.llm.replace('LLM: UKLJUCEN  ', 'LLM: ') : 'mock režim (bez LLM-a)')
        await loadRuns()
        if (cancelled) return       // React StrictMode u razvoju pokrece efekat dva puta
        // link oblika  /?replay=events_....json&speed=2  odmah pusta snimak (zgodno za prezentaciju)
        const q = new URLSearchParams(window.location.search)
        if (q.get('speed')) setSpeed(parseFloat(q.get('speed')) || 1)
        if (q.get('replay')) replay(q.get('replay'))
        else if (r.running) {
          dispatch({ type: 'say', text: 'Simulacija već radi — priključujem se.' })
          dispatch({ type: 'reset' })
          startPolling(0)
        }
      } catch {
        if (!cancelled) setLlmLabel('server nije pokrenut (python app.py)')
      }
    })()
    return () => { cancelled = true; stopPolling() }
  }, [loadRuns, replay, setSpeed, startPolling, stopPolling])

  return {
    state, runStatus, llmLabel, runs, speed, setSpeed,
    start, replay, flightDone,
    busy: runStatus === 'radi…',
  }
}
