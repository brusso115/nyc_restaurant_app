import QueryInput from './QueryInput'
import '../styles/ChatSidebar.css'

function ChatSidebar({ chatHistory, onQuerySubmit }) {
  return (
    <div className="chat-sidebar">
      <div className="chat-history">
        <h2>Chat History</h2>
        <ul>
          {chatHistory.map((msg, i) => (
            <li key={i} className="chat-message">
              <strong>Answer:</strong> {msg.response}
              <br />
              <strong>Sources:</strong>
              <ul>
                {msg.sources.map((s, j) => <li key={j}>{s}</li>)}
              </ul>
            </li>
          ))}
        </ul>
      </div>
      <QueryInput onQuerySubmit={onQuerySubmit} />
    </div>
  )
}

export default ChatSidebar
