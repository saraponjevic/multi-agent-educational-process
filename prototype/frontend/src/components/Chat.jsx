import { useEffect, useRef, useState } from 'react'

// **podebljano** u porukama (bez HTML-a)
function Rich({ text }) {
  return String(text).split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith('**') ? <b key={i}>{part.slice(2, -2)}</b> : <span key={i}>{part}</span>)
}

// Levo: razgovor. Korisnik upise temu, sistem pise sta se desava (faze, artefakti, greske).
export function Chat({ messages, busy, onStart, onOpenArtifact }) {
  const [topic, setTopic] = useState('')
  const box = useRef(null)

  useEffect(() => {
    if (box.current) box.current.scrollTop = box.current.scrollHeight
  }, [messages])

  function submit(e) {
    e.preventDefault()
    const t = topic.trim()
    if (!t) return
    onStart(t)
    setTopic('')
  }

  return (
    <section className="panel chat">
      <h2>Razgovor</h2>
      <div className="messages" ref={box}>
        {messages.map((m) => (
          <div key={m.id} className={`msg ${m.kind}`}>
            {m.kind === 'artifact' ? (
              <>📄 <b>{m.agent}</b> je napravio:{' '}
                <a href="#" onClick={(e) => { e.preventDefault(); onOpenArtifact(m.artKey) }}>{m.title}</a></>
            ) : (
              <Rich text={m.text} />
            )}
            {m.note && <div className="note">{m.note}</div>}
          </div>
        ))}
      </div>
      <form className="ask" onSubmit={submit}>
        <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Želim kurs o …" autoComplete="off" />
        <button type="submit" disabled={busy}>Pokreni</button>
      </form>
    </section>
  )
}
