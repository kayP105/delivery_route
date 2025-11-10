import random
import numpy as np

class GeneticVRP:
    def __init__(self, distance_matrix, population_size=100, generations=200, 
                 mutation_rate=0.02, elite_size=20):
        self.distance_matrix = distance_matrix
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.n_customers = len(distance_matrix) - 1 
    
    def create_individual(self):
        """Create a random route (chromosome)"""
        route = list(range(1, len(self.distance_matrix)))
        random.shuffle(route)
        return [0] + route + [0] 
    def create_population(self):
        """Create initial population"""
        return [self.create_individual() for _ in range(self.population_size)]
    
    def calculate_fitness(self, route):
        """Calculate fitness (inverse of total distance)"""
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += self.distance_matrix[route[i]][route[i+1]]
        return 1 / (total_distance + 0.001)  # Avoid division by zero
    
    def calculate_distance(self, route):
        """Calculate total route distance"""
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += self.distance_matrix[route[i]][route[i+1]]
        return total_distance
    
    def rank_population(self, population):
        """Rank population by fitness"""
        fitness_results = {}
        for i, individual in enumerate(population):
            fitness_results[i] = self.calculate_fitness(individual)
        return sorted(fitness_results.items(), key=lambda x: x[1], reverse=True)
    
    def selection(self, ranked_population):
        """Select parents for mating"""
        selection_results = []
        
        
        for i in range(self.elite_size):
            selection_results.append(ranked_population[i][0])
        
        #
        fitness_sum = sum([fitness for idx, fitness in ranked_population])
        for i in range(self.population_size - self.elite_size):
            pick = random.uniform(0, fitness_sum)
            current = 0
            for idx, fitness in ranked_population:
                current += fitness
                if current >= pick:
                    selection_results.append(idx)
                    break
        
        return selection_results
    
    def breed(self, parent1, parent2):
        """Crossover: Create child from two parents using Order Crossover (OX)"""
        child = [None] * len(parent1)
        child[0] = 0
        child[-1] = 0
        
        # Select a random subset from parent1
        gene_a = random.randint(1, len(parent1) - 2)
        gene_b = random.randint(1, len(parent1) - 2)
        
        start_gene = min(gene_a, gene_b)
        end_gene = max(gene_a, gene_b)
        
        # Copy subset from parent1
        for i in range(start_gene, end_gene):
            child[i] = parent1[i]
        
        # Fill remaining positions from parent2
        child_positions = [i for i in range(1, len(child) - 1) if child[i] is None]
        parent2_genes = [gene for gene in parent2[1:-1] if gene not in child]
        
        for i, pos in enumerate(child_positions):
            if i < len(parent2_genes):
                child[pos] = parent2_genes[i]
        
        return child
    
    def mutate(self, individual):
        """Mutation: Swap two cities with mutation_rate probability"""
        for i in range(1, len(individual) - 1):
            if random.random() < self.mutation_rate:
                j = random.randint(1, len(individual) - 2)
                individual[i], individual[j] = individual[j], individual[i]
        return individual
    
    def breed_population(self, mating_pool, elite_size):
        """Create next generation through breeding"""
        children = []
        pool_size = len(mating_pool)
        
  
        for i in range(elite_size):
            children.append(mating_pool[i])
       
        for i in range(self.population_size - elite_size):
            parent1 = mating_pool[random.randint(0, pool_size - 1)]
            parent2 = mating_pool[random.randint(0, pool_size - 1)]
            child = self.breed(parent1, parent2)
            children.append(child)
        
        return children
    
    def mutate_population(self, population):
        """Apply mutation to entire population"""
        mutated_pop = []
        for individual in population:
            mutated_pop.append(self.mutate(individual))
        return mutated_pop
    
    def next_generation(self, current_gen):
        """Create next generation"""
        ranked_pop = self.rank_population(current_gen)
        selection_results = self.selection(ranked_pop)
        mating_pool = [current_gen[i] for i in selection_results]
        children = self.breed_population(mating_pool, self.elite_size)
        next_gen = self.mutate_population(children)
        return next_gen
    
    def evolve(self):
        """Run genetic algorithm"""
        population = self.create_population()
        best_distances = []
        
        print(f"Starting Genetic Algorithm with {self.generations} generations...")
        
        for generation in range(self.generations):
            population = self.next_generation(population)
            

            ranked = self.rank_population(population)
            best_idx = ranked[0][0]
            best_route = population[best_idx]
            best_distance = self.calculate_distance(best_route)
            best_distances.append(best_distance)
            
            if generation % 20 == 0:
                print(f"Generation {generation}: Best Distance = {best_distance:.2f} km")
        
        # Return best solution
        ranked = self.rank_population(population)
        best_idx = ranked[0][0]
        best_route = population[best_idx]
        best_distance = self.calculate_distance(best_route)
        
        print(f"Final Best Distance: {best_distance:.2f} km")
        
        return best_route, best_distance, best_distances

def apply_genetic_to_clusters(df, distance_matrix):
    """Apply genetic algorithm to each cluster separately"""
    all_routes = []
    total_distance = 0
    
    for cluster_id in df['cluster'].unique():
        if cluster_id == -1:
            continue
        
        cluster_df = df[df['cluster'] == cluster_id].reset_index(drop=True)
        
        if len(cluster_df) < 3:
            route = [0] + list(range(1, len(cluster_df))) + [0]
            distance = sum(distance_matrix[route[i]][route[i+1]] 
                          for i in range(len(route)-1))
        else:
            cluster_indices = df[df['cluster'] == cluster_id].index.tolist()
            cluster_dist_matrix = distance_matrix[np.ix_(cluster_indices, cluster_indices)]
            
            ga = GeneticVRP(cluster_dist_matrix, population_size=50, 
                          generations=100, mutation_rate=0.02)
            route, distance, _ = ga.evolve()
        
        route_coords = [
            {
                'customer_id': int(cluster_df.iloc[i]['customer_id']),
                'latitude': float(cluster_df.iloc[i]['latitude']),
                'longitude': float(cluster_df.iloc[i]['longitude']),
                'position': i
            }
            for i in route
        ]
        
        all_routes.append({
            'cluster_id': int(cluster_id),
            'route': route_coords,
            'distance_km': round(distance, 2)
        })
        total_distance += distance
    
    return all_routes, total_distance
