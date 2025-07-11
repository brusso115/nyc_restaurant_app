import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { useEffect, useState } from 'react'
import { fetchRestaurants } from '../services/api'
import 'leaflet/dist/leaflet.css'
import 'leaflet-defaulticon-compatibility'
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css'
import '../styles/map.css'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN

function RestaurantMap() {
  const [restaurants, setRestaurants] = useState([])

  useEffect(() => {
    fetchRestaurants().then(setRestaurants).catch(console.error)
  }, [])

  return (
    <MapContainer center={[40.73, -73.98]} zoom={13} className="map-container">
      <TileLayer
        url={`https://api.mapbox.com/styles/v1/mapbox/dark-v10/tiles/{z}/{x}/{y}?access_token=${MAPBOX_TOKEN}`}
        tileSize={512}
        zoomOffset={-1}
        attribution='&copy; <a href="https://www.mapbox.com/">Mapbox</a>'
      />
      {restaurants.map((r) => (
        <Marker key={r.id} position={[r.latitude, r.longitude]}>
          <Popup>{r.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}

export default RestaurantMap
