import React from 'react'

const RouteList = ({ routes }) => {
  if (!routes || routes.length === 0) return null

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Optimized Routes</h3>
      {routes.map((route, idx) => (
        <div key={idx} style={styles.routeCard}>
          <div style={styles.routeHeader}>
            Vehicle {route.cluster_id + 1} - {route.distance_km} km
          </div>
          <div style={styles.routeStops}>
            {route.route.map((stop, stopIdx) => (
              <span key={stopIdx} style={styles.stop}>
                {stopIdx > 0 && ' → '}
                Customer {stop.customer_id}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

const styles = {
  container: {
    marginTop: '20px',
    padding: '20px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  },
  title: {
    fontSize: '18px',
    marginBottom: '15px',
    color: '#333'
  },
  routeCard: {
    marginBottom: '15px',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '6px',
    borderLeft: '4px solid #4ECDC4'
  },
  routeHeader: {
    fontWeight: '600',
    fontSize: '16px',
    marginBottom: '10px',
    color: '#333'
  },
  routeStops: {
    fontSize: '14px',
    color: '#666',
    lineHeight: '1.6'
  },
  stop: {
    display: 'inline'
  }
}

export default RouteList
