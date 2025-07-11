import RestaurantMap from '../components/RestaurantMap'
import QueryInput from '../components/QueryInput'
import { useState } from 'react'

function Home() {
  const [response, setResponse] = useState(null)

  return (
    <div style={{ padding: '2rem' }}>
      <h1>NYC Restaurant Explorer</h1>
      <QueryInput onResult={setResponse} />
      <RestaurantMap />

      {response && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Answer</h2>
          <p>{response.answer}</p>
          <h3>Source Menu Items</h3>
          <ul>
            {response.sources.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default Home
