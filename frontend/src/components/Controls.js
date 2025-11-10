import React, { useState } from 'react'

const Controls = ({ onOptimize, loading }) => {
  const [numCustomers, setNumCustomers] = useState(50)
  const [nVehicles, setNVehicles] = useState(5)
  const [method, setMethod] = useState('kmeans')
  const [useGenetic, setUseGenetic] = useState(false)
  const [useTraffic, setUseTraffic] = useState(false)

  const handleOptimize = () => {
    onOptimize(numCustomers, nVehicles, method, useGenetic, useTraffic)
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Route Optimization Controls</h2>
      
      <div style={styles.inputGroup}>
        <label style={styles.label}>Number of Customers:</label>
        <input
          type="number"
          value={numCustomers}
          onChange={(e) => setNumCustomers(parseInt(e.target.value))}
          min="10"
          max="200"
          style={styles.input}
        />
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>Number of Vehicles:</label>
        <input
          type="number"
          value={nVehicles}
          onChange={(e) => setNVehicles(parseInt(e.target.value))}
          min="2"
          max="20"
          style={styles.input}
        />
      </div>

      <div style={styles.inputGroup}>
        <label style={styles.label}>Clustering Method:</label>
        <select
          value={method}
          onChange={(e) => setMethod(e.target.value)}
          style={styles.select}
        >
          <option value="kmeans">K-Means</option>
          <option value="dbscan">DBSCAN</option>
        </select>
      </div>

      <div style={styles.checkboxGroup}>
        <label style={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={useGenetic}
            onChange={(e) => setUseGenetic(e.target.checked)}
            style={styles.checkbox}
          />
          Use Genetic Algorithm
          <span style={styles.badge}>NEW</span>
        </label>
      </div>

      <div style={styles.checkboxGroup}>
        <label style={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={useTraffic}
            onChange={(e) => setUseTraffic(e.target.checked)}
            style={styles.checkbox}
          />
          Real-Time Traffic
          <span style={styles.badge}>NEW</span>
        </label>
        {useTraffic && (
          <p style={styles.hint}>⚠️ Requires Google Maps API key</p>
        )}
      </div>

      <button
        onClick={handleOptimize}
        disabled={loading}
        style={{
          ...styles.button,
          opacity: loading ? 0.6 : 1,
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Optimizing...' : 'Optimize Routes'}
      </button>

      {loading && (
        <div style={styles.loadingText}>
          {useGenetic && '🧬 Running Genetic Algorithm...'}
          {useTraffic && '🚦 Fetching Traffic Data...'}
        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    marginBottom: '20px'
  },
  title: {
    fontSize: '20px',
    marginBottom: '20px',
    color: '#333'
  },
  inputGroup: {
    marginBottom: '15px'
  },
  label: {
    display: 'block',
    marginBottom: '5px',
    fontWeight: '600',
    color: '#555'
  },
  input: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px'
  },
  select: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    backgroundColor: 'white'
  },
  checkboxGroup: {
    marginBottom: '15px',
    padding: '12px',
    backgroundColor: '#fff',
    borderRadius: '6px',
    border: '1px solid #e0e0e0'
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    fontSize: '14px',
    fontWeight: '600',
    color: '#555',
    cursor: 'pointer'
  },
  checkbox: {
    marginRight: '10px',
    width: '18px',
    height: '18px',
    cursor: 'pointer'
  },
  badge: {
    marginLeft: '8px',
    padding: '2px 8px',
    backgroundColor: '#4ECDC4',
    color: 'white',
    fontSize: '10px',
    fontWeight: '700',
    borderRadius: '10px',
    textTransform: 'uppercase'
  },
  hint: {
    marginTop: '8px',
    fontSize: '12px',
    color: '#f39c12',
    fontStyle: 'italic'
  },
  button: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#4ECDC4',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '600',
    marginTop: '10px'
  },
  loadingText: {
    marginTop: '10px',
    textAlign: 'center',
    fontSize: '14px',
    color: '#4ECDC4',
    fontWeight: '600'
  }
}

export default Controls
