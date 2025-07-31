import { useState } from 'react'
import QueryInput from './QueryInput'
import { sendChatMessage } from '../services/api'
import '../styles/ChatSidebar.css'

function ChatSidebar() {
  const [history, setHistory] = useState([])

  const handleSend = async (userMessage) => {
    const updatedHistory = [...history, { role: 'user', content: userMessage }]
    try {
      const data = await sendChatMessage(userMessage, updatedHistory)
      setHistory([
        ...updatedHistory,
        { role: 'assistant', content: data.response }
      ])
    } catch (err) {
      console.error(err)
      setHistory([
        ...updatedHistory,
        { role: 'assistant', content: "Sorry, something went wrong." }
      ])
    }
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
