from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from data_loader import generate_sample_data, create_distance_matrix, load_kaggle_vrp_data
from clustering import DeliveryClusterer
from route_optimizer import VRPOptimizer, nearest_neighbor_heuristic, two_opt
from genetic_algorithm import GeneticVRP, apply_genetic_to_clusters
from traffic_predictor import TrafficPredictor, RealTimeTraffic
import os

app = Flask(__name__)
CORS(app)

os.makedirs('data', exist_ok=True)


GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'YOUR_API_KEY_HERE')
traffic_api = RealTimeTraffic(api_key=GOOGLE_MAPS_API_KEY)

@app.route('/api/generate-data', methods=['POST'])
def generate_data():
    """Generate sample delivery data"""
    num_customers = request.json.get('num_customers', 50)
    df = generate_sample_data(num_customers)
    
    return jsonify({
        'success': True,
        'data': df.to_dict(orient='records'),
        'message': f'Generated {num_customers} delivery locations'
    })

@app.route('/api/cluster', methods=['POST'])
def cluster_deliveries():
    """Perform clustering on delivery locations"""
    data = request.json
    df = pd.DataFrame(data['deliveries'])
    method = data.get('method', 'kmeans')
    n_vehicles = data.get('n_vehicles', 5)
    
    clusterer = DeliveryClusterer(df)
    
    if method == 'kmeans':
        df, centers = clusterer.kmeans_cluster(n_vehicles)
        result = {
            'clustered_data': df.to_dict(orient='records'),
            'centers': centers.tolist(),
            'method': 'K-Means'
        }
    else:
        df, n_clusters, n_outliers = clusterer.dbscan_cluster()
        result = {
            'clustered_data': df.to_dict(orient='records'),
            'n_clusters': n_clusters,
            'n_outliers': n_outliers,
            'method': 'DBSCAN'
        }
    
    df = clusterer.balance_vehicle_capacity(vehicle_capacity=300)
    
    return jsonify({
        'success': True,
        'result': result,
        'balanced_data': df.to_dict(orient='records')
    })

@app.route('/api/optimize-routes', methods=['POST'])
def optimize_routes():
    """Optimize routes using 2-Opt heuristic"""
    data = request.json
    df = pd.DataFrame(data['deliveries'])
    
    distance_matrix = create_distance_matrix(df)
    
    all_routes = []
    total_distance_before = 0
    total_distance_after = 0
    
    for cluster_id in df['cluster'].unique():
        if cluster_id == -1:
            continue
        
        cluster_df = df[df['cluster'] == cluster_id].reset_index(drop=True)
        
        if len(cluster_df) < 2:
            continue
        
        cluster_indices = df[df['cluster'] == cluster_id].index.tolist()
        cluster_dist_matrix = distance_matrix[np.ix_(cluster_indices, cluster_indices)]
        
        nn_route, nn_distance = nearest_neighbor_heuristic(cluster_dist_matrix)
        total_distance_before += nn_distance
        
        opt_route, opt_distance = two_opt(nn_route, cluster_dist_matrix)
        total_distance_after += opt_distance
        
        route_coords = [
            {
                'customer_id': int(cluster_df.iloc[i]['customer_id']),
                'latitude': float(cluster_df.iloc[i]['latitude']),
                'longitude': float(cluster_df.iloc[i]['longitude']),
                'position': i
            }
            for i in opt_route
        ]
        
        all_routes.append({
            'cluster_id': int(cluster_id),
            'route': route_coords,
            'distance_km': round(opt_distance, 2),
            'improvement': round(((nn_distance - opt_distance) / nn_distance * 100), 2)
        })
    
    improvement = round(((total_distance_before - total_distance_after) / total_distance_before * 100), 2)
    
    return jsonify({
        'success': True,
        'routes': all_routes,
        'total_distance_before_km': round(total_distance_before, 2),
        'total_distance_after_km': round(total_distance_after, 2),
        'improvement_percent': improvement
    })

@app.route('/api/optimize-genetic', methods=['POST'])
def optimize_genetic():
    """Optimize routes using Genetic Algorithm"""
    data = request.json
    df = pd.DataFrame(data['deliveries'])
    use_traffic = data.get('use_traffic', False)
    
    if use_traffic:
        print("Using traffic-adjusted distances for genetic algorithm...")
        distance_matrix = traffic_api.update_distance_matrix_with_traffic(df, sample_size=20)
    else:
        distance_matrix = create_distance_matrix(df)
    
    all_routes, total_distance = apply_genetic_to_clusters(df, distance_matrix)
    
    return jsonify({
        'success': True,
        'routes': all_routes,
        'total_distance_km': round(total_distance, 2),
        'method': 'Genetic Algorithm',
        'traffic_enabled': use_traffic
    })

@app.route('/api/traffic-analysis', methods=['POST'])
def traffic_analysis():
    """Analyze traffic patterns"""
    predictor = TrafficPredictor()
    traffic_patterns = predictor.generate_traffic_patterns()
    
    hours = list(range(24))
    patterns = [
        {'hour': h, 'multiplier': round(traffic_patterns[h], 2)}
        for h in hours
    ]
    
    return jsonify({
        'success': True,
        'traffic_patterns': patterns
    })

@app.route('/api/full-optimization', methods=['POST'])
def full_optimization():
    """Complete optimization pipeline with comparison"""
    data = request.json
    num_customers = data.get('num_customers', 50)
    n_vehicles = data.get('n_vehicles', 5)
    method = data.get('clustering_method', 'kmeans')
    use_genetic = data.get('use_genetic', False)
    use_traffic = data.get('use_traffic', False)
    
    df = generate_sample_data(num_customers)
    
    clusterer = DeliveryClusterer(df)
    if method == 'kmeans':
        df, _ = clusterer.kmeans_cluster(n_vehicles)
    else:
        df, _, _ = clusterer.dbscan_cluster()
    
    df = clusterer.balance_vehicle_capacity()
 
    if use_traffic:
        print("Fetching real-time traffic data...")
        distance_matrix = traffic_api.update_distance_matrix_with_traffic(df, sample_size=20)
    else:
        distance_matrix = create_distance_matrix(df)
    
  
    before_routes = []
    before_total_distance = 0
    
    for cluster_id in df['cluster'].unique():
        if cluster_id == -1:
            continue
        
        cluster_df = df[df['cluster'] == cluster_id].reset_index(drop=True)
        if len(cluster_df) < 2:
            continue
        
        cluster_indices = df[df['cluster'] == cluster_id].index.tolist()
        cluster_dist_matrix = distance_matrix[np.ix_(cluster_indices, cluster_indices)]
        
        nn_route, nn_distance = nearest_neighbor_heuristic(cluster_dist_matrix)
        before_total_distance += nn_distance
        
        route_coords = [
            {
                'customer_id': int(cluster_df.iloc[i]['customer_id']),
                'latitude': float(cluster_df.iloc[i]['latitude']),
                'longitude': float(cluster_df.iloc[i]['longitude'])
            }
            for i in nn_route
        ]
        
        before_routes.append({
            'cluster_id': int(cluster_id),
            'route': route_coords,
            'distance_km': round(nn_distance, 2)
        })
    
   
    after_routes = []
    after_total_distance = 0
    
    if use_genetic:
        print("Running Genetic Algorithm optimization...")
        after_routes, after_total_distance = apply_genetic_to_clusters(df, distance_matrix)
        optimization_method = "Genetic Algorithm"
    else:
        print("Running 2-Opt optimization...")
        for cluster_id in df['cluster'].unique():
            if cluster_id == -1:
                continue
            
            cluster_df = df[df['cluster'] == cluster_id].reset_index(drop=True)
            if len(cluster_df) < 2:
                continue
            
            cluster_indices = df[df['cluster'] == cluster_id].index.tolist()
            cluster_dist_matrix = distance_matrix[np.ix_(cluster_indices, cluster_indices)]
            
            nn_route, _ = nearest_neighbor_heuristic(cluster_dist_matrix)
            opt_route, opt_distance = two_opt(nn_route, cluster_dist_matrix)
            after_total_distance += opt_distance
            
            route_coords = [
                {
                    'customer_id': int(cluster_df.iloc[i]['customer_id']),
                    'latitude': float(cluster_df.iloc[i]['latitude']),
                    'longitude': float(cluster_df.iloc[i]['longitude'])
                }
                for i in opt_route
            ]
            
            after_routes.append({
                'cluster_id': int(cluster_id),
                'route': route_coords,
                'distance_km': round(opt_distance, 2)
            })
        
        optimization_method = "2-Opt Heuristic"
    
    improvement_percent = round(((before_total_distance - after_total_distance) / before_total_distance * 100), 2)
    
    return jsonify({
        'success': True,
        'deliveries': df.to_dict(orient='records'),
        'before_routes': before_routes,
        'after_routes': after_routes,
        'before_distance_km': round(before_total_distance, 2),
        'after_distance_km': round(after_total_distance, 2),
        'improvement_percent': improvement_percent,
        'num_vehicles': len(after_routes),
        'optimization_method': optimization_method,
        'traffic_enabled': use_traffic
    })

if __name__ == '__main__':
    print("="*50)
    print("Delivery Route Optimizer Backend")
    print("="*50)
    if traffic_api.enabled:
        print("✓ Real-time traffic API: ENABLED")
    else:
        print("✗ Real-time traffic API: DISABLED (using synthetic traffic)")
        print("  To enable: Set GOOGLE_MAPS_API_KEY environment variable")
    print("="*50)
    app.run(debug=True, port=5000)
