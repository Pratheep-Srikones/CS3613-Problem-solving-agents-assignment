import re
import random
import copy
# first we consider cities as 0,1,2,3.... then in the end we assign 0 - a, 1 - b ,.....

def process_input_file(filename):
    city_map = []
    trucks = []

    with open(filename, 'r') as file:
        # Read the matrix (city map)
        for line in file:
            line = line.strip()
            if line:  # Ensure the line is not empty
                if '#' in line:  # This line is truck information
                    trucks.append(line)
                    break
                # Convert the line into a list of integers or 'N'
                row = line.split(',')
                city_map.append([int(value) if value != 'N' else 'N' for value in row])
        
        # Read the truck information
        for line in file:
            line = line.strip()
            if line:  # Ensure the line is not empty
                trucks.append(line)

    return city_map, trucks

def create_adjacency_dictionary(city_map):
    adjacency_dictionary = {}

    for i in range(len(city_map)):
        adjacent_cities = []
        for j in range(len(city_map[i])):
            if city_map[i][j] != 'N' and city_map[i][j] != 0:  # Exclude 'N' and self-loops
                adjacent_cities.append(j)
        adjacency_dictionary[i] = adjacent_cities

    return adjacency_dictionary

def parse_trucks(raw_trucks):
    truck_dictionary = {}  # Use a dictionary instead of a list

    for raw_truck in raw_trucks:
        match = re.match(r'truck_(\d+)#(\d+)', raw_truck)
        if match:
            truck_id = f"truck_{match.group(1)}"
            capacity = int(match.group(2))
            truck_dictionary[truck_id] = [None] * capacity  # Create a list with 'capacity' length
    return truck_dictionary


def assign_random_cities(truck_assignments, num_cities):
    city_indices = list(range(1,num_cities))  # Include 0 as well to match total cities count
    random.shuffle(city_indices)  # Shuffle once for unique assignments

    # Assign cities to each truck based on its capacity
    start = 0
    for truck_id, cities in truck_assignments.items():
        capacity = len(cities)  # Capacity of the truck is the current list length
        truck_assignments[truck_id] = city_indices[start:start + capacity]  # Assign unique cities
        start += capacity  # Move the starting point for the next truck

    return truck_assignments

# generate random solution
def assign_valid_random_cities(truck_assignments, num_cities, city_map):
    # Create the adjacency dictionary from the city map
    adjacency_dict = create_adjacency_dictionary(city_map)
    
    city_indices = list(range(1, num_cities))  # List of cities (excluding city 0)
    assigned_cities = {0}  # To keep track of cities already assigned
    
    for truck_id, cities in truck_assignments.items():
        assigned_route = []  # List to store the assigned cities for this truck
        start_city = 0  # All trucks start from city 0
        
        # Try assigning cities to the truck until a valid route is found
        while len(assigned_route) < len(cities):
            # Get a list of cities that are adjacent to the current city (and not yet assigned)
            possible_cities = [city for city in adjacency_dict[start_city] if city not in assigned_cities]
            
            if not possible_cities:
                # If no valid cities are available, restart the assignment for this truck
                assigned_route = []  # Reset the truck's route and try again
                assigned_cities.clear()  # Clear all assigned cities to start fresh
                break
            
            # Randomly choose a valid city from the possible cities
            next_city = random.choice(possible_cities)
            assigned_route.append(next_city)
            assigned_cities.add(next_city)
            start_city = next_city  # Move to the next city

        # If a valid route was assigned, update the truck's route
        if assigned_route:
            truck_assignments[truck_id] = assigned_route
    
    return truck_assignments


def calculate_total_cost(truck_assignments, city_map):
    total_cost = 0

    for truck_id, cities in truck_assignments.items():
        if not cities:
            return f"Visit not possible for {truck_id} due to no assigned cities."

        truck_cost = 0

        # Start from city 0 to the first city in the truck's list
        if cities[0] == None:
            return f"Visit not possible for {truck_id} due to truck does not get assinged any cites"
        
        truck_cost = city_map[0][cities[0]]

        if truck_cost == 'N':
            return f"Visit not possible for {truck_id} due to no path from city {0} to city {cities[0]}."
        
        for i in range(len(cities) - 1):
            distance = city_map[cities[i]][cities[i+1]]
            if distance == 'N':
                return f"Visit not possible for {truck_id} due to no path from city {cities[i]} to city {cities[i+1]}."
            truck_cost += distance  # Add distance to truck's total cost

        total_cost += truck_cost  # Add truck's cost to total cost

    return total_cost

def hill_climbing(truck_assignments, city_map, maxIterations=100):
    # Initial optimum cost
    optimum_cost = calculate_total_cost(truck_assignments, city_map)
    best_neighbours = [truck_assignments]  # Track the best assignments found
    current_assignments = truck_assignments

    for _ in range(maxIterations):
        # Create a deep copy of the current assignments to modify
        new_truck_assignments = copy.deepcopy(current_assignments)

        # Select two different trucks at random
        truck_ids = random.sample(list(new_truck_assignments.keys()), 2)
        truck1, truck2 = truck_ids[0], truck_ids[1]
        cities1, cities2 = new_truck_assignments[truck1], new_truck_assignments[truck2]

        # Make sure both trucks have at least one city assigned
        if cities1 and cities2:
            # Randomly select one city from each truck to swap
            idx1 = random.randint(0, len(cities1) - 1)
            idx2 = random.randint(0, len(cities2) - 1)

            # Swap the selected cities between the two trucks
            cities1[idx1], cities2[idx2] = cities2[idx2], cities1[idx1]

        # Calculate the new cost
        cost = calculate_total_cost(new_truck_assignments, city_map)

        # Skip this assignment if the cost is a string (indicating a visit is not possible)
        if isinstance(cost, str):
            continue
        
        # If the new cost is better, update the optimum
        if cost < optimum_cost:
            best_neighbours.append(new_truck_assignments)
            optimum_cost = cost
            current_assignments = new_truck_assignments  # Update the current assignment to the best found

    return best_neighbours, optimum_cost

def main():
    filename = 'input.txt'
    city_map, raw_trucks = process_input_file(filename)

    # Output the results
    print("City Map (n x n Matrix):")
    for row in city_map:
        print(row)

    print("\nTruck Information:")
    for truck in raw_trucks:
        print(truck)

    truck_dictionary = parse_trucks(raw_trucks)
    print("Truck Dictionary", truck_dictionary)
    truck_assignments = assign_valid_random_cities(truck_dictionary, len(city_map), city_map)
    # print("Truck Dictionary", truck_dictionary)
    # total_cost = calculate_total_cost(truck_assignments, city_map)
    # print("total cost", total_cost)

    print(hill_climbing(truck_assignments, city_map))

if __name__ == '__main__':
    main()
