#Delivery Route Optimizer

An intelligent delivery route optimization system that combines **unsupervised machine learning** (K-Means, DBSCAN) with **advanced optimization algorithms** (Genetic Algorithm, 2-Opt) to reduce delivery distances by 15-25% while respecting real-world constraints.


Problem Statement

Traditional delivery routing leads to:
- **Inefficient routes** with excessive travel distance
- **Vehicle overloading** without capacity planning
- **Ignoring traffic patterns** causing delays
- **No visual comparison** of optimization impact

This project solves these problems using a **two-stage optimization approach**.

---

Key Features

Machine Learning & Optimization
- **K-Means Clustering** - Groups customers into geographic zones
- **DBSCAN Clustering** - Density-based grouping with outlier detection
- **Genetic Algorithm** - Evolutionary optimization (100+ generations)
- **2-Opt Heuristic** - Local search improvement
- **Nearest Neighbor** - Initial route construction

 Real-World Constraints
- **Vehicle Capacity Limits** - Automatic cluster balancing
- **Time Windows** - Customer availability constraints
- **Traffic Patterns** - Rush hour simulation (synthetic)
- **Distance Optimization** - Haversine distance calculation

Visualization & Analysis
- **Interactive Maps** (React + Leaflet + OpenStreetMap)
- **Before/After Comparison** - Visual proof of improvement
- **Route Statistics** - Distance, vehicle count, improvement %
- **Per-Route Breakdown** - Individual vehicle performance



