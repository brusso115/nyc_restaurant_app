export async function fetchRestaurants() {
  const res = await fetch('/restaurants')
  if (!res.ok) throw new Error('Failed to fetch restaurants')
  return res.json()
}

export async function fetchCategories() {
  const res = await fetch('/categories')
  if (!res.ok) throw new Error('Failed to fetch categories')
  return res.json()
}

export async function sendChatMessage(query, history = []) {
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, history })
  })

  if (!res.ok) throw new Error('Failed to send chat message')
  return res.json()
}
