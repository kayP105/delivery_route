import React from 'react'

const Statistics = ({ stats, beforeRoutes, afterRoutes }) => {
  if (!stats) return null

  const improvementColor = stats.improvement_percent > 0 ? '#27ae60' : '#e74c3c'

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Optimization Results</h2>
      
      <div style={styles.grid}>
        <div style={styles.card}>
          <div style={styles.cardLabel}>Before Optimization</div>
          <div style={{...styles.cardValue, color: '#e74c3c'}}>
            {stats.before_distance_km} km
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardLabel}>After Optimization</div>
          <div style={{...styles.cardValue, color: '#27ae60'}}>
            {stats.after_distance_km} km
          </div>
        </div>

        <div style={{...styles.card, backgroundColor: '#e8f8f5'}}>
          <div style={styles.cardLabel}>Improvement</div>
          <div style={{...styles.cardValue, color: improvementColor}}>
            ↓ {stats.improvement_percent}%
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardLabel}>Vehicles Used</div>
          <div style={styles.cardValue}>{stats.num_vehicles}</div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardLabel}>Total Deliveries</div>
          <div style={styles.cardValue}>{stats.deliveries?.length || 0}</div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardLabel}>Method</div>
          <div style={{...styles.cardValue, fontSize: '14px'}}>
            {stats.optimization_method}
          </div>
        </div>
      </div>

      {stats.traffic_enabled && (
        <div style={styles.trafficBanner}>
          🚦 Real-time traffic data used in calculations
        </div>
      )}

      {afterRoutes && afterRoutes.length > 0 && (
        <div style={styles.routeList}>
          <h3 style={styles.subtitle}>Route Details</h3>
          {afterRoutes.map((route, idx) => {
            const beforeRoute = beforeRoutes?.find(r => r.cluster_id === route.cluster_id)
            const routeImprovement = beforeRoute 
              ? ((beforeRoute.distance_km - route.distance_km) / beforeRoute.distance_km * 100).toFixed(1)
              : 0

            return (
              <div key={idx} style={styles.routeItem}>
                <div style={styles.routeHeader}>
                  <strong>Vehicle {route.cluster_id + 1}</strong>
                  <span style={styles.routeDistance}>
                    {beforeRoute && (
                      <span style={{textDecoration: 'line-through', color: '#999', marginRight: '8px'}}>
                        {beforeRoute.distance_km} km
                      </span>
                    )}
                    <span style={{color: '#27ae60', fontWeight: '700'}}>
                      {route.distance_km} km
                    </span>
                    {routeImprovement > 0 && (
                      <span style={{color: '#27ae60', fontSize: '12px', marginLeft: '8px'}}>
                        (↓{routeImprovement}%)
                      </span>
                    )}
                  </span>
                </div>
                <div style={styles.routeStops}>
                  {route.route.length} stops
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    padding: '20px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginTop: '20px'
  },
  title: {
    fontSize: '20px',
    marginBottom: '20px',
    color: '#333'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '15px',
    marginBottom: '20px'
  },
  card: {
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    textAlign: 'center'
  },
  cardLabel: {
    fontSize: '12px',
    color: '#666',
    marginBottom: '8px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  },
  cardValue: {
    fontSize: '22px',
    fontWeight: '700',
    color: '#4ECDC4'
  },
  trafficBanner: {
    padding: '12px',
    backgroundColor: '#fff3cd',
    border: '1px solid #ffc107',
    borderRadius: '6px',
    textAlign: 'center',
    fontSize: '14px',
    fontWeight: '600',
    color: '#856404',
    marginBottom: '20px'
  },
  routeList: {
    marginTop: '20px'
  },
  subtitle: {
    fontSize: '16px',
    marginBottom: '10px',
    color: '#555'
  },
  routeItem: {
    padding: '12px',
    backgroundColor: '#f8f9fa',
    borderRadius: '6px',
    marginBottom: '8px',
    borderLeft: '4px solid #4ECDC4'
  },
  routeHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '5px',
    fontSize: '14px'
  },
  routeDistance: {
    fontSize: '14px'
  },
  routeStops: {
    fontSize: '12px',
    color: '#666'
  }
}

export default Statistics

