// GLAVNA KOMPONENTA - slaze stranicu od delova.
//
//   Header        gore: LLM rezim, status, brzina, snimci
//   Chat          levo: unos teme + sta se desava
//   Phases        faze 1-4
//   PhaseBoard    tok izabrane faze (agenti, aktivnosti, petlja)
//   Classroom     nastavnik -> ucenici (tackice), znanje i ocene
//   Artifacts     desno: sta su agenti napravili
//
// Svo stanje dolazi iz hook-a useSimulation (simulation/useSimulation.js).

import { useCallback, useMemo, useState } from 'react'
import { Artifacts, ArtifactModal, EventLog } from './components/Artifacts.jsx'
import { Chat } from './components/Chat.jsx'
import { Classroom } from './components/Classroom.jsx'
import { Header } from './components/Header.jsx'
import { PhaseBoard } from './components/PhaseBoard.jsx'
import { Phases } from './components/Phases.jsx'
import { useSimulation } from './simulation/useSimulation.js'

export default function App() {
  const sim = useSimulation()
  const { state } = sim
  const [selectedPhase, setSelectedPhase] = useState(null)   // rucni izbor faze (inace prati trenutnu)
  const [openArtifact, setOpenArtifact] = useState(null)

  const latestByAgent = useMemo(() => {
    const m = new Map()
    for (const a of state.artifacts) if (!m.has(a.id)) m.set(a.id, a)   // lista je najnovije-prvo
    return m
  }, [state.artifacts])

  const openByKey = useCallback((key) => setOpenArtifact(state.artifacts.find((a) => a.key === key) || null),
    [state.artifacts])
  const closeArtifact = useCallback(() => setOpenArtifact(null), [])

  // kad pocne nova faza, prikaz prati nju
  const [followedPhase, setFollowedPhase] = useState(null)
  if (state.selected !== followedPhase) {
    setFollowedPhase(state.selected)
    setSelectedPhase(null)
  }
  const shownPhase = selectedPhase || state.selected

  return (
    <>
      <Header llmLabel={sim.llmLabel} runStatus={sim.runStatus} speed={sim.speed} setSpeed={sim.setSpeed}
              runs={sim.runs} onReplay={sim.replay} />
      <main>
        <Chat messages={state.messages} busy={sim.busy} onStart={sim.start} onOpenArtifact={openByKey} />

        <div className="col">
          {state.system ? (
            <>
              <Phases system={state.system} current={state.current} selected={shownPhase}
                      phaseDone={state.phaseDone} status={state.status} feedback={state.feedback}
                      onSelect={setSelectedPhase} />
              <PhaseBoard system={state.system} selected={shownPhase} status={state.status}
                          rounds={state.rounds} total={state.total}
                          artifactIds={new Set(latestByAgent.keys())}
                          onOpenAgent={(id) => setOpenArtifact(latestByAgent.get(id))} />
              <Classroom system={state.system} students={state.students} total={state.total}
                         blackboard={state.blackboard} flights={state.flights} speed={sim.speed}
                         onFlightDone={sim.flightDone} />
            </>
          ) : (
            <section className="panel"><span className="empty">Učitavam opis sistema sa servera…</span></section>
          )}
        </div>

        {state.system && <Artifacts system={state.system} artifacts={state.artifacts} onOpen={setOpenArtifact} />}
      </main>
      <EventLog lines={state.log} />
      {openArtifact && <ArtifactModal key={openArtifact.key} artifact={openArtifact} onClose={closeArtifact} />}
    </>
  )
}
