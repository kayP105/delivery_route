import React, { useState } from 'react'
import MapView from './components/MapView'
import Controls from './components/Controls'
import Statistics from './components/Statistics'
import RouteList from './components/RouteList'
import { fullOptimization } from './services/api'

function App() {
  const [deliveries, setDeliveries] = useState([])
  const [beforeRoutes, setBeforeRoutes] = useState([])
  const [afterRoutes, setAfterRoutes] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showBefore, setShowBefore] = useState(true)
  const [showAfter, setShowAfter] = useState(true)

  const handleOptimize = async (numCustomers, nVehicles, method, useGenetic, useTraffic) => {
    setLoading(true)
    try {
      const result = await fullOptimization(numCustomers, nVehicles, method, useGenetic, useTraffic)
      
      if (result.success) {
        setDeliveries(result.deliveries)
        setBeforeRoutes(result.before_routes)
        setAfterRoutes(result.after_routes)
        setStats({
          before_distance_km: result.before_distance_km,
          after_distance_km: result.after_distance_km,
          improvement_percent: result.improvement_percent,
          num_vehicles: result.num_vehicles,
          deliveries: result.deliveries,
          optimization_method: result.optimization_method,
          traffic_enabled: result.traffic_enabled
        })
      }
    } catch (error) {
      console.error('Optimization failed:', error)
      alert('Optimization failed. Make sure backend is running on port 5000.')
    }
    setLoading(false)
  }

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.headerTitle}>🚚 Delivery Route Optimizer</h1>
        <p style={styles.headerSubtitle}>
          K-Means | DBSCAN | Genetic Algorithm | Real-Time Traffic | Before/After Comparison
        </p>
      </header>

      <div style={styles.container}>
        <div style={styles.sidebar}>
          <Controls onOptimize={handleOptimize} loading={loading} />
          
          {stats && (
            <div style={styles.toggleContainer}>
              <h3 style={styles.toggleTitle}>Map Display Options</h3>
              <label style={styles.toggleLabel}>
                <input
                  type="checkbox"
                  checked={showBefore}
                  onChange={(e) => setShowBefore(e.target.checked)}
                  style={styles.checkbox}
                />
                Show Before Routes (Red Dashed)
              </label>
              <label style={styles.toggleLabel}>
                <input
                  type="checkbox"
                  checked={showAfter}
                  onChange={(e) => setShowAfter(e.target.checked)}
                  style={styles.checkbox}
                />
                Show After Routes (Colored Solid)
              </label>
            </div>
          )}
          
          <Statistics stats={stats} beforeRoutes={beforeRoutes} afterRoutes={afterRoutes} />
        </div>

        <div style={styles.main}>
          {deliveries.length > 0 ? (
            <>
              <MapView 
                deliveries={deliveries} 
                beforeRoutes={beforeRoutes}
                afterRoutes={afterRoutes}
                showBefore={showBefore}
                showAfter={showAfter}
              />
              <RouteList routes={afterRoutes} />
            </>
          ) : (
            <div style={styles.placeholder}>
              <h2>Welcome to Route Optimizer Pro</h2>
              <p>Configure parameters and click "Optimize Routes" to begin</p>
              <div style={styles.features}>
                <div style={styles.feature}>🧬 Genetic Algorithm</div>
                <div style={styles.feature}>🚦 Real-Time Traffic</div>
                <div style={styles.feature}>📊 Before/After Comparison</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#f0f2f5'
  },
  header: {
    backgroundColor: '#4ECDC4',
    color: 'white',
    padding: '30px 20px',
    textAlign: 'center',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  headerTitle: {
    margin: 0,
    fontSize: '32px',
    fontWeight: '700'
  },
  headerSubtitle: {
    margin: '10px 0 0 0',
    fontSize: '14px',
    opacity: 0.9
  },
  container: {
    display: 'grid',
    gridTemplateColumns: '350px 1fr',
    gap: '20px',
    padding: '20px',
    maxWidth: '1600px',
    margin: '0 auto'
  },
  sidebar: {
    display: 'flex',
    flexDirection: 'column'
  },
  main: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  placeholder: {
    textAlign: 'center',
    padding: '100px 20px',
    color: '#999'
  },
  features: {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginTop: '30px'
  },
  feature: {
    padding: '10px 20px',
    backgroundColor: '#4ECDC4',
    color: 'white',
    borderRadius: '20px',
    fontSize: '14px',
    fontWeight: '600'
  },
  toggleContainer: {
    padding: '15px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    marginTop: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  toggleTitle: {
    fontSize: '14px',
    fontWeight: '700',
    marginBottom: '12px',
    color: '#333'
  },
  toggleLabel: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '14px',
    fontWeight: '600',
    color: '#555',
    cursor: 'pointer',
    marginBottom: '10px'
  },
  checkbox: {
    marginRight: '10px',
    width: '18px',
    height: '18px',
    cursor: 'pointer'
  }
}

export default App
