import React from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png'
})

const COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2', '#F39C12', '#E74C3C']

const MapView = ({ deliveries, beforeRoutes, afterRoutes, showBefore, showAfter }) => {
  const center = deliveries.length > 0 
    ? [deliveries[0].latitude, deliveries[0].longitude]
    : [13.0, 77.6]

  return (
    <div style={{ height: '600px', width: '100%', border: '2px solid #ddd', borderRadius: '8px', position: 'relative' }}>
      <MapContainer center={center} zoom={12} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Customer locations */}
        {deliveries.map((delivery, idx) => (
          <CircleMarker
            key={idx}
            center={[delivery.latitude, delivery.longitude]}
            radius={8}
            fillColor={COLORS[delivery.cluster % COLORS.length]}
            color="#fff"
            weight={2}
            opacity={1}
            fillOpacity={0.8}
          >
            <Popup>
              <strong>Customer {delivery.customer_id}</strong><br/>
              Cluster: {delivery.cluster}<br/>
              Demand: {delivery.demand}<br/>
              Time Window: {delivery.time_window_start}:00 - {delivery.time_window_end}:00
            </Popup>
          </CircleMarker>
        ))}

        {/* BEFORE routes (dashed red lines) */}
        {showBefore && beforeRoutes && beforeRoutes.map((route, idx) => {
          const positions = route.route.map(point => [point.latitude, point.longitude])
          
          return (
            <Polyline
              key={`before-${idx}`}
              positions={positions}
              color="#FF0000"
              weight={3}
              opacity={0.5}
              dashArray="10, 10"
            />
          )
        })}

        {/* AFTER routes (solid colored lines) */}
        {showAfter && afterRoutes && afterRoutes.map((route, idx) => {
          const positions = route.route.map(point => [point.latitude, point.longitude])
          const color = COLORS[route.cluster_id % COLORS.length]
          
          return (
            <Polyline
              key={`after-${idx}`}
              positions={positions}
              color={color}
              weight={4}
              opacity={0.8}
            />
          )
        })}
      </MapContainer>
      
      {/* Legend */}
      <div style={styles.legend}>
        {showBefore && (
          <div style={styles.legendItem}>
            <div style={{...styles.legendLine, background: '#FF0000', borderStyle: 'dashed'}}></div>
            <span>Before Optimization</span>
          </div>
        )}
        {showAfter && (
          <div style={styles.legendItem}>
            <div style={{...styles.legendLine, background: '#4ECDC4'}}></div>
            <span>After Optimization</span>
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  legend: {
    position: 'absolute',
    bottom: '20px',
    right: '20px',
    background: 'white',
    padding: '15px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
    zIndex: 1000
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '8px',
    fontSize: '14px'
  },
  legendLine: {
    width: '30px',
    height: '3px',
    marginRight: '10px',
    borderRadius: '2px'
  }
}

export default MapView

