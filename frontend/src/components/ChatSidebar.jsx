import { useState } from 'react'
import QueryInput from './QueryInput'
import '../styles/ChatSidebar.css'

function ChatSidebar() {
  const [history, setHistory] = useState([])

  const handleSend = async (userMessage) => {
    const updated = [...history, { role: 'user', content: userMessage }]

    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: userMessage,
        history: updated
      })
    })

    const data = await res.json()
    setHistory([...updated, { role: 'assistant', content: data.response }])
  }

  return (
    <div className="chat-sidebar">
      <div className="chat-history">
        <h2>Chat</h2>
        {history.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : 'Bot'}:</strong> {msg.content}
          </div>
        ))}
      </div>
      <QueryInput onSend={handleSend} />
    </div>
  )
}

export default ChatSidebar
