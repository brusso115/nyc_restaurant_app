import '../styles/Home.css'
import RestaurantMap from '../components/RestaurantMap'
import ChatSidebar from '../components/ChatSidebar'

function Home() {

  return (
    <div className="home-page">
      <div className="main-layout">
        <div className="map-container">
          <RestaurantMap />
        </div>
        <div className="chat-container">
          <ChatSidebar/>
        </div>
      </div>
    </div>
  )
}

export default Home
