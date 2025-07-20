export async function fetchRestaurants() {
  const res = await fetch('/restaurants')
  if (!res.ok) throw new Error('Failed to fetch restaurants')
  return res.json()
}

export async function runQueryWithHistory(query, history = []) {
  const cleanedHistory = history.map(turn => ({
    query: String(turn.query ?? ""),
    response: String(turn.response ?? ""),
    sources: Array.isArray(turn.sources)
      ? turn.sources.map(s => String(s))
      : []
  }))

  const body = {
    query,
    filters: {},
    history: cleanedHistory
  }

  const res = await fetch('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })

  if (!res.ok) {
    const error = await res.text()
    console.error("Backend error:", error)
    throw new Error("Query failed: " + error)
  }

  return res.json()
}


export async function fetchCategories() {
  const res = await fetch('/categories')
  if (!res.ok) throw new Error('Failed to fetch categories')
  return res.json()
}