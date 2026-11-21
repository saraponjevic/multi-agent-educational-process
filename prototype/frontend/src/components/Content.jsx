// Prikaz sadrzaja artefakata:
//   <Markdown text="..."/>   - fajlovi kurikulum.md, lekcije.md, izvestaj.md ...
//   <ValueView value={...}/> - bilo koji JSON izlaz agenta kao citljiva lista/kartice

const esc = (s) =>
  String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])

// Vrlo jednostavan markdown: naslovi, liste, tabele, kod blokovi, **podebljano**, `kod`.
// Tekst se PRVO escape-uje, pa tek onda dobija oznake - zato je dangerouslySetInnerHTML ovde bezbedan.
function markdownToHtml(text) {
  const inline = (s) =>
    esc(s)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
      .replace(/(^|\s)\*(\S.*?)\*/g, '$1<i>$2</i>')
  const out = []
  let table = null
  let code = null
  for (const raw of String(text).split('\n')) {
    const line = raw.trimEnd()
    if (line.trim().startsWith('```')) {
      if (code) { out.push(`<pre><code>${esc(code.join('\n'))}</code></pre>`); code = null }
      else code = []
      continue
    }
    if (code) { code.push(raw); continue }
    if (/^\s*\|/.test(line)) {
      if (/^\s*\|[\s\-:|]+\|\s*$/.test(line)) continue
      const cells = line.trim().replace(/^\||\|$/g, '').split('|').map((c) => `<td>${inline(c.trim())}</td>`).join('')
      ;(table ||= []).push(`<tr>${cells}</tr>`)
      continue
    }
    if (table) { out.push(`<table>${table.join('')}</table>`); table = null }
    const h = line.match(/^(#{1,4})\s+(.*)/)
    if (h) out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`)
    else if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
      const pad = (line.search(/\S/) / 2) * 12 + 8
      out.push(`<div style="padding-left:${pad}px">• ${inline(line.replace(/^\s*([-*]|\d+\.)\s+/, ''))}</div>`)
    } else if (line.startsWith('>')) out.push(`<blockquote>${inline(line.replace(/^>\s?/, ''))}</blockquote>`)
    else if (line === '---') out.push('<hr>')
    else if (line) out.push(`<p>${inline(line)}</p>`)
  }
  if (code) out.push(`<pre><code>${esc(code.join('\n'))}</code></pre>`)
  if (table) out.push(`<table>${table.join('')}</table>`)
  return out.join('')
}

export function Markdown({ text }) {
  return <div className="md" dangerouslySetInnerHTML={{ __html: markdownToHtml(text) }} />
}

const HIDDEN_KEYS = new Set(['files', 'received_from', 'segments'])

export function ValueView({ value, depth = 0 }) {
  if (value == null || value === '') return <span className="empty">—</span>
  if (typeof value !== 'object') {
    const s = String(value)
    return s.includes('\n') ? <Markdown text={s} /> : <>{s}</>
  }
  if (Array.isArray(value)) {
    if (!value.length) return <span className="empty">(prazno)</span>
    if (value.every((x) => x == null || typeof x !== 'object')) return <>{value.join(', ')}</>
    return value.map((x, i) => (
      <div className="card" key={i}><ValueView value={x} depth={depth + 1} /></div>
    ))
  }
  if (depth > 5) return <pre>{JSON.stringify(value, null, 1)}</pre>
  const rows = Object.entries(value).filter(([k]) => !k.startsWith('_') && !HIDDEN_KEYS.has(k))
  return (
    <dl>
      {rows.map(([k, v]) => (
        <div className="row" key={k}>
          <dt>{k}</dt>
          <dd><ValueView value={v} depth={depth + 1} /></dd>
        </div>
      ))}
    </dl>
  )
}
