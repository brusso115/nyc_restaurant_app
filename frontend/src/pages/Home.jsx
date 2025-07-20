import '../styles/Home.css'
import RestaurantMap from '../components/RestaurantMap'
import ChatSidebar from '../components/ChatSidebar'
import { useState } from 'react'
import { runQueryWithHistory } from '../services/api'

function Home() {
  const [chatHistory, setChatHistory] = useState([])

  const handleQuerySubmit = async (query) => {
    console.log("📤 Submitting query:", query)
    try {
      const result = await runQueryWithHistory(query, chatHistory)
      console.log("✅ Received result:", result)
      const newTurn = {
        query: String(query),
        response: result.answer,
        sources: Array.isArray(result.sources) ? result.sources.map(String) : []
      }
      setChatHistory(prev => [...prev, newTurn])
    } catch (err) {
      console.error('Server error:', err)
    }
  }

  return (
    <div className="home-page">
      <div className="main-layout">
        <div className="map-container">
          <RestaurantMap />
        </div>
        <div className="chat-container">
          <ChatSidebar chatHistory={chatHistory} onQuerySubmit={handleQuerySubmit} />
        </div>
      </div>
    </div>
  )
}

export default Home
