export async function fetchRestaurants() {
  const res = await fetch('/restaurants')
  if (!res.ok) throw new Error('Failed to fetch restaurants')
  return res.json()
}

export async function runQuery(query) {
  const res = await fetch('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  })
  if (!res.ok) throw new Error('Failed to run query')
  return res.json()
}
