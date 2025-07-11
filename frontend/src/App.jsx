import { useState } from 'react'

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const res = await fetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      const data = await res.json()
      setResponse(data)
    } catch (err) {
      console.error('Error:', err)
      setResponse({ answer: 'Error connecting to server', sources: [] })
    }

    setLoading(false)
  }

  return (
    <div style={{ padding: '2rem', maxWidth: 600, margin: '0 auto' }}>
      <h1>Menu Recommender</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="What are you in the mood for?"
          style={{ width: '100%', padding: '0.5rem', fontSize: '1rem' }}
        />
        <button type="submit" style={{ marginTop: '1rem' }}>Submit</button>
      </form>

      {loading && <p>Loading...</p>}

      {response && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Answer</h2>
          <p>{response.answer}</p>

          <h3>Source Menu Items</h3>
          <ul>
            {response.sources.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App
