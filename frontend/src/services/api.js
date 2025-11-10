import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export const generateData = async (numCustomers) => {
  const response = await axios.post(`${API_URL}/generate-data`, {
    num_customers: numCustomers
  })
  return response.data
}

export const clusterDeliveries = async (deliveries, method, nVehicles) => {
  const response = await axios.post(`${API_URL}/cluster`, {
    deliveries,
    method,
    n_vehicles: nVehicles
  })
  return response.data
}

export const optimizeRoutes = async (deliveries) => {
  const response = await axios.post(`${API_URL}/optimize-routes`, {
    deliveries
  })
  return response.data
}

export const fullOptimization = async (numCustomers, nVehicles, method, useGenetic, useTraffic) => {
  const response = await axios.post(`${API_URL}/full-optimization`, {
    num_customers: numCustomers,
    n_vehicles: nVehicles,
    clustering_method: method,
    use_genetic: useGenetic,
    use_traffic: useTraffic
  })
  return response.data
}

export const getTrafficAnalysis = async () => {
  const response = await axios.post(`${API_URL}/traffic-analysis`)
  return response.data
}
