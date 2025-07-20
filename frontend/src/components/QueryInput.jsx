import { useState } from 'react'

function QueryInput({ onQuerySubmit }) {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)

    await onQuerySubmit(query)

    setLoading(false)
    setQuery('')
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
