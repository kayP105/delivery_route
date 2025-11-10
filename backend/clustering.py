from sklearn.cluster import KMeans, DBSCAN
import numpy as np

class DeliveryClusterer:
    def __init__(self, df):
        self.df = df
        self.coordinates = df[['latitude', 'longitude']].values
        
    def kmeans_cluster(self, n_vehicles=5):
        kmeans = KMeans(n_clusters=n_vehicles, random_state=42, n_init=10)
        labels = kmeans.fit_predict(self.coordinates)
        self.df['cluster'] = labels
        return self.df, kmeans.cluster_centers_
    
    def dbscan_cluster(self, eps=0.05, min_samples=3):
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(self.coordinates)
        self.df['cluster'] = labels
        
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_outliers = list(labels).count(-1)
        
        return self.df, n_clusters, n_outliers
    
    def balance_vehicle_capacity(self, vehicle_capacity=200):
        for cluster_id in self.df['cluster'].unique():
            if cluster_id == -1:
                continue
            
            cluster_demand = self.df[self.df['cluster'] == cluster_id]['demand'].sum()
            
            if cluster_demand > vehicle_capacity:
                cluster_df = self.df[self.df['cluster'] == cluster_id]
                n_vehicles_needed = int(np.ceil(cluster_demand / vehicle_capacity))
                
                sub_kmeans = KMeans(n_clusters=n_vehicles_needed, random_state=42)
                sub_labels = sub_kmeans.fit_predict(
                    cluster_df[['latitude', 'longitude']].values
                )
                
                max_cluster = self.df['cluster'].max()
                new_labels = sub_labels + max_cluster + 1
                self.df.loc[self.df['cluster'] == cluster_id, 'cluster'] = new_labels
        
        return self.df
