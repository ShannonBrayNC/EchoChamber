import { useEffect, useState } from 'react'

const API = 'http://localhost:8000'

export default function App() {
  const [runs, setRuns] = useState([])
  const [summary, setSummary] = useState(null)
  const [selected, setSelected] = useState(null)
  const workspace = 'default'

  useEffect(() => {
    fetch(`${API}/workspaces/${workspace}/runs`)
      .then(res => res.json())
      .then(data => {
        setRuns(data.runs || [])
        setSummary(data.summary)
      })
  }, [])

  const replay = async (runId) => {
    const res = await fetch(`${API}/workspaces/${workspace}/runs/${runId}/replay`, {
      method: 'POST'
    })
    const data = await res.json()
    setSelected(data)
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>EchoChamber Command Center</h1>

      {summary && (
        <div>
          <h3>Summary</h3>
          <p>Total: {summary.totalRuns} | OK: {summary.okRuns} | Failed: {summary.failedRuns}</p>
        </div>
      )}

      <h3>Runs</h3>
      <table border="1">
        <thead>
          <tr>
            <th>Run ID</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {runs.map(r => (
            <tr key={r.runId}>
              <td>{r.runId}</td>
              <td>{r.status}</td>
              <td>
                <button onClick={() => replay(r.runId)}>Replay</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selected && (
        <div>
          <h3>Replay Result</h3>
          <pre>{JSON.stringify(selected.intelligence, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
