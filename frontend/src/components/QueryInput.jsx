import { useState } from 'react'
import { runQuery } from '../services/api'

function QueryInput({ onResult }) {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const result = await runQuery(query)
      onResult(result)
    } catch (err) {
      console.error(err)
      onResult({ answer: 'Server error', sources: [] })
    }
    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="What are you in the mood for?"
        style={{ width: '100%', padding: '0.5rem', fontSize: '1rem' }}
      />
      <button type="submit" style={{ marginTop: '0.5rem' }}>
        {loading ? 'Searching...' : 'Submit'}
      </button>
    </form>
  )
}

export default QueryInput
