import { useEffect, useState } from 'react'

const API = 'http://localhost:8000'

export default function InboxIntelligence() {
  const workspace = 'default'
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch(`${API}/inbox/${workspace}`)
      .then(res => res.json())
      .then(setData)
  }, [])

  if (!data) return <div>Loading...</div>

  const { coverage, exceptions, classificationBuckets } = data

  return (
    <div className="app-shell">
      <h2>Inbox Intelligence</h2>

      <div className="grid">
        <div className="card">
          <div className="metric-label">Coverage</div>
          <div className="metric-value">{coverage.coveragePercent}%</div>
        </div>

        <div className="card">
          <div className="metric-label">Exceptions</div>
          <div className="metric-value">{coverage.exceptionCount}</div>
        </div>

        <div className="card">
          <div className="metric-label">High Confidence</div>
          <div className="metric-value">{coverage.highConfidenceMessages}</div>
        </div>
      </div>

      <div className="content-grid">
        <div className="card">
          <h3>Exceptions</h3>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Confidence</th>
                  <th>Reasons</th>
                </tr>
              </thead>
              <tbody>
                {exceptions.map(e => (
                  <tr key={e.messageId}>
                    <td>{e.subject}</td>
                    <td>{e.confidence}</td>
                    <td>{e.reasons.join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <h3>Classification</h3>
          <ul>
            {classificationBuckets.map(b => (
              <li key={b.classification}>
                {b.classification}: {b.count}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
