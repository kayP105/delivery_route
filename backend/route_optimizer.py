from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np

class VRPOptimizer:
    def __init__(self, distance_matrix, demands, vehicle_capacity, num_vehicles):
        self.distance_matrix = distance_matrix
        self.demands = demands
        self.vehicle_capacity = vehicle_capacity
        self.num_vehicles = num_vehicles
        
    def create_data_model(self):
        """Store problem data"""
        data = {}
        data['distance_matrix'] = (self.distance_matrix * 1000).astype(int).tolist()
        data['demands'] = self.demands.tolist()
        data['vehicle_capacities'] = [self.vehicle_capacity] * self.num_vehicles
        data['num_vehicles'] = self.num_vehicles
        data['depot'] = 0
        return data
    
    def solve(self):
        """Solve VRP using OR-Tools"""
        data = self.create_data_model()
        
        manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']),
            data['num_vehicles'],
            data['depot']
        )
        
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            data['vehicle_capacities'],
            True,
            'Capacity'
        )
        
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 30
        
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            return self.extract_routes(data, manager, routing, solution)
        return None
    
    def extract_routes(self, data, manager, routing, solution):
        """Extract route information from solution"""
        routes = []
        total_distance = 0
        
        for vehicle_id in range(data['num_vehicles']):
            if not routing.IsVehicleUsed(solution, vehicle_id):
                continue
                
            route = []
            route_distance = 0
            index = routing.Start(vehicle_id)
            
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route.append(node)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            
            route.append(manager.IndexToNode(index))
            
            routes.append({
                'vehicle_id': vehicle_id,
                'route': route,
                'distance_meters': route_distance
            })
            total_distance += route_distance
        
        return {
            'routes': routes,
            'total_distance': total_distance,
            'objective_value': solution.ObjectiveValue()
        }

def nearest_neighbor_heuristic(distance_matrix, start=0):
    """Simple nearest neighbor algorithm"""
    n = len(distance_matrix)
    unvisited = set(range(n))
    unvisited.remove(start)
    
    route = [start]
    current = start
    total_distance = 0
    
    while unvisited:
        nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
        total_distance += distance_matrix[current][nearest]
        route.append(nearest)
        current = nearest
        unvisited.remove(nearest)
    
    total_distance += distance_matrix[current][start]
    route.append(start)
    
    return route, total_distance

def two_opt(route, distance_matrix):
    """2-opt improvement heuristic"""
    improved = True
    best_route = route[:]
    best_distance = calculate_route_distance(route, distance_matrix)
    
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1:
                    continue
                
                new_route = route[:]
                new_route[i:j] = reversed(route[i:j])
                new_distance = calculate_route_distance(new_route, distance_matrix)
                
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
        
        route = best_route
    
    return best_route, best_distance

def calculate_route_distance(route, distance_matrix):
    """Calculate total route distance"""
    return sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
