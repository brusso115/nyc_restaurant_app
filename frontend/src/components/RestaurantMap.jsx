import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { useEffect, useState, useMemo } from 'react'
import { fetchRestaurants, fetchCategories } from '../services/api'
import CategoryDropdown from './CategoryDropdown'
import 'leaflet/dist/leaflet.css'
import 'leaflet-defaulticon-compatibility'
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css'
import '../styles/map.css'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN

function RestaurantMap() {
  const [restaurants, setRestaurants] = useState([])
  const [selectedCategories, setSelectedCategories] = useState([])
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [categories, setCategories] = useState([])

  useEffect(() => {
    Promise.all([fetchRestaurants(), fetchCategories()])
      .then(([restaurantsData, categoryList]) => {
        setRestaurants(restaurantsData)
        setSelectedCategories(categoryList.map(c => c.name))
        setCategories(categoryList.map(c => c.name)) // add a new state for available categories
      })
      .catch(console.error)
  }, [])

  const filtered = restaurants.filter(
    r => r.categories?.some(cat => selectedCategories.includes(cat))
  )

  return (
    <div className="restaurant-map-container">
      <CategoryDropdown
        categories={categories}
        selected={selectedCategories}
        onChange={setSelectedCategories}
        open={dropdownOpen}
        setOpen={setDropdownOpen}
      />

      <div className="map-wrapper">
        <MapContainer
          center={[40.73, -73.98]}
          zoom={13}
          className="map-container"
        >
          <TileLayer
            url={`https://api.mapbox.com/styles/v1/mapbox/dark-v10/tiles/{z}/{x}/{y}?access_token=${MAPBOX_TOKEN}`}
            tileSize={512}
            zoomOffset={-1}
            attribution='&copy; <a href="https://www.mapbox.com/">Mapbox</a>'
          />
          {filtered.map((r) => (
            <Marker
              key={r.id}
              position={[r.latitude, r.longitude]}
              icon={L.divIcon({
                className: 'custom-marker',
                iconSize: [16, 16],
              })}
            >
              <Popup>{r.name}</Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  )
}

export default RestaurantMap