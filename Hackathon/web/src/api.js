const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    // FastAPI puts the friendly message in `detail`; keep it, drop the status code.
    throw new Error(body.detail || `Request failed (${res.status})`)
  }
  return body
}

export const getSamples = () => request('/samples')

export const searchTopics = (q = '') =>
  request(`/topics?q=${encodeURIComponent(q)}`)

export const getPractice = (topic) =>
  request('/practice', { method: 'POST', body: JSON.stringify({ topic }) })

export const startSession = (problem) =>
  request('/session', { method: 'POST', body: JSON.stringify({ problem }) })

export const getHint = (sid, level) => request(`/session/${sid}/hint/${level}`)

export const checkWorking = (sid, working) =>
  request(`/session/${sid}/diagnose`, {
    method: 'POST',
    body: JSON.stringify({ working }),
  })

export const askTutor = (sid, question) =>
  request(`/session/${sid}/ask`, {
    method: 'POST',
    body: JSON.stringify({ question }),
  })

export const getComparison = (sid) => request(`/session/${sid}/compare`)
