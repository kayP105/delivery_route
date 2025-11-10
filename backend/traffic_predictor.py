import numpy as np
from sklearn.linear_model import LinearRegression
import googlemaps
from datetime import datetime
import os

class TrafficPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.trained = False
    
    def generate_traffic_patterns(self, hours=24):
        """Generate synthetic traffic multipliers for each hour"""
        peak_morning = 9
        peak_evening = 18
        
        traffic = []
        for hour in range(hours):
            if 7 <= hour <= 10:
                multiplier = 1.0 + 0.5 * np.exp(-((hour - peak_morning)**2) / 4)
            elif 16 <= hour <= 20:
                multiplier = 1.0 + 0.6 * np.exp(-((hour - peak_evening)**2) / 4)
            else:
                multiplier = 1.0
            traffic.append(multiplier)
        
        return traffic
    
    def adjust_distance_for_traffic(self, distance, hour):
        """Adjust distance based on traffic at given hour"""
        traffic_patterns = self.generate_traffic_patterns()
        return distance * traffic_patterns[hour]
    
    def predict_delivery_time(self, distance_km, hour, avg_speed_kmh=40):
        """Predict delivery time considering traffic"""
        adjusted_distance = self.adjust_distance_for_traffic(distance_km, hour)
        time_hours = adjusted_distance / avg_speed_kmh
        return time_hours * 60


class RealTimeTraffic:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        
        if self.api_key and self.api_key != 'YOUR_API_KEY_HERE':
            try:
                self.gmaps = googlemaps.Client(key=self.api_key)
                self.enabled = True
                print("✓ Real-time traffic API enabled")
            except:
                self.enabled = False
                print("✗ Google Maps API key invalid, using synthetic traffic")
        else:
            self.enabled = False
            print("✗ No API key provided, using synthetic traffic patterns")
    
    def get_travel_time_with_traffic(self, origin_lat, origin_lon, 
                                     dest_lat, dest_lon, departure_time=None):
    
        if not self.enabled:
            return None
        
        try:
            if departure_time is None:
                departure_time = datetime.now()
            
            result = self.gmaps.directions(
                origin=(origin_lat, origin_lon),
                destination=(dest_lat, dest_lon),
                mode="driving",
                departure_time=departure_time,
                traffic_model="best_guess"
            )
            
            if result and len(result) > 0:
               
                duration_seconds = result[0]['legs'][0]['duration_in_traffic']['value']
            
                distance_meters = result[0]['legs'][0]['distance']['value']
                
                return {
                    'duration_minutes': duration_seconds / 60,
                    'distance_km': distance_meters / 1000,
                    'traffic_delay': (duration_seconds - 
                                    result[0]['legs'][0]['duration']['value']) / 60
                }
        except Exception as e:
            print(f"Traffic API error: {e}")
            return None
        
        return None
    
    def update_distance_matrix_with_traffic(self, df, sample_size=None):
       
        if not self.enabled:
            print("Using synthetic traffic (no API key)")
            return self.synthetic_traffic_matrix(df)
        
        n = len(df)
        if sample_size and n > sample_size:
            print(f"Sampling {sample_size} locations to save API calls")
            n = sample_size
        
        traffic_matrix = np.zeros((n, n))
        api_calls = 0
        max_calls = 100  
        
        print(f"Fetching real-time traffic for {n}x{n} = {n*n} routes...")
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    traffic_matrix[i][j] = 0
                    continue
                
                if api_calls >= max_calls:
                    print(f"Reached API call limit ({max_calls}), using synthetic for rest")
                    return self.synthetic_traffic_matrix(df)
                
                origin_lat = df.iloc[i]['latitude']
                origin_lon = df.iloc[i]['longitude']
                dest_lat = df.iloc[j]['latitude']
                dest_lon = df.iloc[j]['longitude']
                
                result = self.get_travel_time_with_traffic(
                    origin_lat, origin_lon, dest_lat, dest_lon
                )
                
                if result:
                    traffic_matrix[i][j] = result['distance_km']
                    api_calls += 1
                else:
                
                    from data_loader import haversine_distance
                    traffic_matrix[i][j] = haversine_distance(
                        origin_lat, origin_lon, dest_lat, dest_lon
                    )
            
            if (i + 1) % 5 == 0:
                print(f"  Processed {i+1}/{n} locations ({api_calls} API calls)")
        
        print(f"✓ Real-time traffic matrix created ({api_calls} API calls used)")
        return traffic_matrix
    
    def synthetic_traffic_matrix(self, df):
        """Fallback: Generate synthetic traffic-adjusted distances"""
        from data_loader import create_distance_matrix
        base_matrix = create_distance_matrix(df)

        current_hour = datetime.now().hour
        predictor = TrafficPredictor()
        traffic_patterns = predictor.generate_traffic_patterns()
        multiplier = traffic_patterns[current_hour]
        
        print(f"Current hour: {current_hour}:00, Traffic multiplier: {multiplier:.2f}x")
        return base_matrix * multiplier
