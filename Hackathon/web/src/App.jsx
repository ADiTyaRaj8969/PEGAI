import { useEffect, useState } from 'react'
import {
  getSamples, searchTopics, getPractice,
  startSession, getHint, checkWorking, askTutor, getComparison,
} from './api'
import './App.css'

const LEVEL_NAMES = { 1: 'Orient', 2: 'Set up', 3: 'Walk through' }
const LEVEL_BLURB = {
  1: 'Concept only — no equation, no arithmetic.',
  2: 'The setup — which value goes where, but not the result.',
  3: 'The method with real numbers, stopping before the last step.',
}

function Banner({ kind, children }) {
  if (!children) return null
  return <div className={`banner ${kind}`}>{children}</div>
}

function LeakBadge({ hint }) {
  if (!hint.guarded) {
    return (
      <div className="badge neutral">
        Level 3 may approach the answer — not guarded by design
      </div>
    )
  }
  return hint.leak_detected ? (
    <div className="badge warn">
      Leak detected ({hint.leak_where}) — hint regenerated before display
    </div>
  ) : (
    <div className="badge ok">
      Leak check passed — alias, numeric and equation scan
    </div>
  )
}

function HintCard({ hint }) {
  return (
    <article className="card hint">
      <header className="hint-head">
        <span className="pill">Hint {hint.level} of 3</span>
        <span className="level-name">{LEVEL_NAMES[hint.level]}</span>
      </header>
      <p className="hint-text">{hint.hint}</p>
      <p className="blurb">{LEVEL_BLURB[hint.level]}</p>
      <LeakBadge hint={hint} />
    </article>
  )
}

function Diagnosis({ result }) {
  if (!result) return null
  const { status, first_wrong_step, what_they_did, why_wrong, targeted_hint } = result
  const tone = status === 'correct' ? 'ok' : status === 'incomplete' ? 'info' : 'warn'
  const heading =
    status === 'correct' ? 'Every step checks out.'
      : status === 'incomplete' ? 'No mistakes so far — but you have not finished yet.'
        : `First mistake: step ${first_wrong_step ?? '?'}`

  return (
    <div className="card inner">
      <div className={`badge ${tone}`}>{heading}</div>
      {what_they_did && <p className="meta"><strong>What you did:</strong> {what_they_did}</p>}
      {why_wrong && <p className="meta"><strong>Why it does not work:</strong> {why_wrong}</p>}
      {targeted_hint && <p className="hint-text">{targeted_hint}</p>}
    </div>
  )
}

function TopicSearch({ onPick, picking }) {
  const [query, setQuery] = useState('')
  const [topics, setTopics] = useState([])
  const [open, setOpen] = useState(false)

  // Debounced so typing does not fire a request per keystroke.
  useEffect(() => {
    const t = setTimeout(() => {
      searchTopics(query).then(setTopics).catch(() => setTopics([]))
    }, 180)
    return () => clearTimeout(t)
  }, [query])

  return (
    <div className="topic-search">
      <label htmlFor="topic">Search topics</label>
      <input
        id="topic"
        value={query}
        onFocus={() => setOpen(true)}
        onChange={(e) => { setQuery(e.target.value); setOpen(true) }}
        placeholder="e.g. integrals, probability, trigonometry, matrices…"
        autoComplete="off"
      />
      {open && topics.length > 0 && (
        <>
          <div className="topic-count">
            {topics.length} topic{topics.length === 1 ? '' : 's'}
            {query ? ` matching “${query}”` : ' available'}
          </div>
          <ul className="topic-list">
            {topics.map((t) => (
              <li key={t.slug}>
                <button
                  type="button"
                  className="topic-chip"
                  disabled={!!picking}
                  onClick={() => { onPick(t); setOpen(false); setQuery(t.label) }}
                >
                  {t.label}
                  {t.sample
                    ? <span className="chip-tag ready">sample</span>
                    : <span className="chip-tag gen">generate</span>}
                </button>
              </li>
            ))}
          </ul>
        </>
      )}
      {open && query && topics.length === 0 && (
        <div className="topic-count">No topic matches “{query}”.</div>
      )}
    </div>
  )
}

export default function App() {
  const [samples, setSamples] = useState([])
  const [problem, setProblem] = useState('')
  const [picking, setPicking] = useState('')
  const [sid, setSid] = useState(null)
  const [topic, setTopic] = useState(null)
  const [hints, setHints] = useState([])
  const [working, setWorking] = useState('')
  const [diag, setDiag] = useState(null)
  const [question, setQuestion] = useState('')
  const [askReply, setAskReply] = useState(null)
  const [cmp, setCmp] = useState(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')

  useEffect(() => { getSamples().then(setSamples).catch(() => {}) }, [])

  const reset = () => {
    setSid(null); setHints([]); setDiag(null); setCmp(null)
    setWorking(''); setAskReply(null); setQuestion(''); setTopic(null)
  }

  async function pickTopic(topic) {
    setError('')
    if (topic.sample) {                       // canned problem — instant
      setProblem(topic.sample)
      return
    }
    setPicking(`Writing a practice problem on ${topic.label}…`)
    try {
      const p = await getPractice(topic.slug)
      setProblem(p.problem)
    } catch (e) { setError(e.message) } finally { setPicking('') }
  }

  async function start() {
    setError(''); reset(); setBusy('Reading the problem and writing hints…')
    try {
      const s = await startSession(problem)
      setSid(s.session_id); setTopic(s.topic)
      setHints([await getHint(s.session_id, 1)])
    } catch (e) { setError(e.message) } finally { setBusy('') }
  }

  async function nextHint() {
    setError(''); setBusy('Checking the next hint for leaks…')
    try {
      setHints([...hints, await getHint(sid, hints.length + 1)])
    } catch (e) { setError(e.message) } finally { setBusy('') }
  }

  async function check() {
    setError(''); setDiag(null); setBusy('Reading your working…')
    try { setDiag(await checkWorking(sid, working)) }
    catch (e) { setError(e.message) } finally { setBusy('') }
  }

  async function ask() {
    setError(''); setAskReply(null)
    try { setAskReply(await askTutor(sid, question)) }
    catch (e) { setError(e.message) }
  }

  async function compare() {
    setError(''); setBusy('Running V1 and V2 on the same problem…')
    try { setCmp(await getComparison(sid)) }
    catch (e) { setError(e.message) } finally { setBusy('') }
  }

  return (
    <div className="page">
      <header className="masthead">
        <h1>Hint-Based Math Tutor</h1>
        <p>Guiding students to the answer — never handing it over</p>
        <div className="tags">
          <span>Team 5</span><span>Problem 13</span><span>Theme C</span>
        </div>
      </header>

      <section className="card">
        <TopicSearch picking={picking} onPick={pickTopic} />
        {picking && <div className="badge info">{picking}</div>}

        <label htmlFor="sample">Or choose a sample problem</label>
        <select id="sample" defaultValue=""
          onChange={(e) => setProblem(e.target.value)}>
          <option value="">— type your own —</option>
          {samples.map((s) => (
            <option key={s.label} value={s.problem}>{s.label}</option>
          ))}
        </select>

        <label htmlFor="problem">Problem</label>
        <textarea id="problem" rows={3} value={problem}
          onChange={(e) => setProblem(e.target.value)}
          placeholder="Paste any school-level word problem…" />

        <div className="row">
          <button className="primary" onClick={start} disabled={!!busy}>
            Start tutoring
          </button>
          {topic && <span className="topic">detected topic: {topic}</span>}
        </div>
      </section>

      <Banner kind="warn">{error}</Banner>
      <Banner kind="info">{busy}</Banner>

      {hints.map((h) => <HintCard key={h.level} hint={h} />)}

      {sid && hints.length < 3 && (
        <button className="secondary wide" onClick={nextHint} disabled={!!busy}>
          Show hint {hints.length + 1}
        </button>
      )}
      {sid && hints.length === 3 && (
        <p className="meta center">That is all three hints — the last step is yours.</p>
      )}

      {sid && (
        <section className="card">
          <h2>Ask the tutor</h2>
          <div className="row">
            <input value={question} onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. just tell me the answer" />
            <button className="secondary" onClick={ask}>Ask</button>
          </div>
          {askReply && (
            <div className={`badge ${askReply.refused ? 'warn' : 'info'}`}>
              {askReply.message}
            </div>
          )}
        </section>
      )}

      {sid && (
        <section className="card">
          <h2>Check my working</h2>
          <textarea rows={4} value={working}
            onChange={(e) => setWorking(e.target.value)}
            placeholder={'speed = distance x time\nspeed = 120 x 2 = 240'} />
          <button className="secondary" onClick={check} disabled={!!busy}>
            Check my steps
          </button>
          <Diagnosis result={diag} />
        </section>
      )}

      {sid && (
        <section className="card">
          <h2>V1 vs V2</h2>
          <button className="secondary" onClick={compare} disabled={!!busy}>
            Compare versions
          </button>
          {cmp && (
            <div className="compare">
              <div>
                <h3>V1 — single prompt</h3>
                <p className="blurb">
                  Zero-shot. One instruction not to reveal the answer. No verification.
                </p>
                <pre>{cmp.v1_raw}</pre>
                <div className="badge warn">
                  No programmatic check — a leak here reaches the student.
                </div>
              </div>
              <div>
                <h3>V2 — decomposed and guarded</h3>
                <p className="blurb">
                  Solve, then hint, then verify. Five techniques, deterministic guard.
                </p>
                {cmp.v2.map((h) => (
                  <p key={h.level} className="hint-text">
                    <strong>L{h.level}</strong> {h.hint}
                  </p>
                ))}
                <div className="badge ok">
                  Every L1 and L2 hint passed the leak guard before display.
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      <footer className="foot">
        Prompt Engineering for Generative AI · Marwadi University
      </footer>
    </div>
  )
}
