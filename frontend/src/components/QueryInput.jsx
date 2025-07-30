import { useState } from 'react'

function QueryInput({ onSend }) {
  const [input, setInput] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return
    await onSend(input)
    setInput('')
  }

  return (
    <form className="query-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about food, dishes, cravings..."
      />
      <button type="submit">Send</button>
    </form>
  )
}

export default QueryInput
