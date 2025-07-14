import '../styles/Home.css'
import RestaurantMap from '../components/RestaurantMap'
import ChatSidebar from '../components/ChatSidebar'
import { useState } from 'react'

function Home() {
  const [chatHistory, setChatHistory] = useState([])
  const [response, setResponse] = useState(null)

  const handleQueryResult = (result) => {
    setChatHistory([...chatHistory, result])
    setResponse(result)
  }

  return (
    <div className="home-page">
      <div className="main-layout">
        <div className="map-container">
          <RestaurantMap />
        </div>
        <div className="chat-container">
          <ChatSidebar chatHistory={chatHistory} onQuery={handleQueryResult} />
        </div>
      </div>
    </div>
  )
}

export default Home
