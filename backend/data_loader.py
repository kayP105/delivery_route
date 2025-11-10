import vrplib
import numpy as np
import pandas as pd
import os

def download_cvrplib_instance(instance_name="X-n101-k25"):
    """Download instance from CVRPLIB"""
    try:
        instance = vrplib.download_instance(f"{instance_name}.vrp")
        solution = vrplib.download_solution(f"{instance_name}.sol")
        return instance, solution
    except:
        print("Using sample data instead")
        return generate_sample_data()

def generate_sample_data(num_customers=50):
    """Generate synthetic delivery data"""
    np.random.seed(42)
    
    data = {
        'customer_id': range(num_customers),
        'latitude': np.random.uniform(12.9, 13.1, num_customers),
        'longitude': np.random.uniform(77.5, 77.7, num_customers),
        'demand': np.random.randint(5, 50, num_customers),
        'time_window_start': np.random.randint(8, 12, num_customers),
        'time_window_end': np.random.randint(14, 20, num_customers),
        'service_time': np.random.randint(10, 30, num_customers)
    }
    
    df = pd.DataFrame(data)
    df.to_csv('data/delivery_locations.csv', index=False)
    return df

def load_kaggle_vrp_data(filepath):
    """Load VRP data from Kaggle CSV"""
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return generate_sample_data()

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km"""
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def create_distance_matrix(df):
    """Create distance matrix from coordinates"""
    n = len(df)
    matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = haversine_distance(
                    df.iloc[i]['latitude'], df.iloc[i]['longitude'],
                    df.iloc[j]['latitude'], df.iloc[j]['longitude']
                )
    return matrix
