import pygame
import random
import math
import numpy as np
import sys
import time

from numpy.random import randint

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ant Colony Optimization - Traveling Salesman")

# Surface for pheromone trails with alpha support
trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Constants for ACO
NUM_CITIES = 37
NUM_ANTS = 100
NUM_ITERATIONS = 400
EVAPORATION_RATE = 0.1
PHEROMONE_INTENSITY = 1.0
ALPHA = 1  # Importance of pheromone
BETA = 2  # Importance of distance

# Generate random cities
cities = [(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(NUM_CITIES)]
city_distances = [[math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) for x2, y2 in cities] for x1, y1 in cities]

# Initialize pheromone levels
pheromones = np.ones((NUM_CITIES, NUM_CITIES))


# Function for ant's path selection based on pheromones and distances
def choose_next_city(current_city, visited):
    probabilities = []
    for next_city in range(NUM_CITIES):
        if next_city not in visited:
            tau = pheromones[current_city][next_city] ** ALPHA
            eta = (1 / city_distances[current_city][next_city]) ** BETA
            probabilities.append(tau * eta)
        else:
            probabilities.append(0)

    probabilities = np.array(probabilities)
    return np.random.choice(range(NUM_CITIES), p=probabilities / probabilities.sum())


# Function for ant to find a path
def ant_find_path():
    path = []
    visited = set()
    current_city = random.randint(0, NUM_CITIES - 1)
    path.append(current_city)
    visited.add(current_city)

    while len(visited) < NUM_CITIES:
        next_city = choose_next_city(current_city, visited)
        path.append(next_city)
        visited.add(next_city)
        current_city = next_city

    return path


# Calculate path distance
def path_distance(path):
    return sum(city_distances[path[i]][path[i + 1]] for i in range(len(path) - 1)) + city_distances[path[-1]][path[0]]


# Update pheromones based on paths
def update_pheromones(paths, best_path):
    global pheromones
    pheromones *= (1 - EVAPORATION_RATE)  # Evaporation
    for path in paths:
        distance = path_distance(path)
        for i in range(len(path) - 1):
            pheromones[path[i]][path[i + 1]] += PHEROMONE_INTENSITY / distance
        pheromones[path[-1]][path[0]] += PHEROMONE_INTENSITY / distance  # Close loop


# Main loop for ACO
best_path = None
best_distance = float('inf')
running = True

for iteration in range(NUM_ITERATIONS):
    if not running:
        break

    # Generate paths for all ants in the current iteration
    paths = [ant_find_path() for _ in range(NUM_ANTS)]

    # Calculate distances for each path
    path_distances = [path_distance(path) for path in paths]

    # Find the best path in this iteration
    min_dist_idx = np.argmin(path_distances)
    if path_distances[min_dist_idx] < best_distance:
        best_distance = path_distances[min_dist_idx]
        best_path = paths[min_dist_idx]

    # Update pheromones based on current paths
    update_pheromones(paths, best_path)

    # Pygame visualization
    screen.fill(WHITE)
    trail_surface.fill((0, 0, 0, 0))  # Clear trail surface with transparency

    # Draw cities
    for city in cities:
        pygame.draw.circle(screen, BLUE, city, 5)

    # Draw pheromone trails
    max_pheromone = np.max(pheromones)
    for i in range(NUM_CITIES):
        for j in range(i + 1, NUM_CITIES):
            pheromone_level = pheromones[i][j]
            if pheromone_level > 0:  # Draw only for paths with pheromones
                # Normalize pheromone level to 0-255 for transparency
                alpha = int((pheromone_level / max_pheromone) * 255)
                color = (0, 0, 0, alpha)  # Black with variable opacity
                start_pos = cities[i]
                end_pos = cities[j]
                pygame.draw.line(trail_surface, color, start_pos, end_pos, 2)

    # Blit trail surface onto the main screen
    screen.blit(trail_surface, (0, 0))

    # Draw current best path
    if best_path:
        for i in range(len(best_path) - 1):
            pygame.draw.line(screen, RED, cities[best_path[i]], cities[best_path[i + 1]], 2)
        pygame.draw.line(screen, RED, cities[best_path[-1]], cities[best_path[0]], 2)  # Close the loop

    # Display shortest distance
    font = pygame.font.SysFont(None, 30)
    text = font.render(f"Iteration {iteration + 1}/{NUM_ITERATIONS} - Shortest Distance: {best_distance:.2f}", True,
                       BLACK)
    screen.blit(text, (20, 20))

    pygame.display.flip()

    # Handle events to keep the window responsive
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Add a short delay to allow visualization of the process
    #time.sleep(0.00001)

# Keep the window open after completing the iterations
finished = True
while finished:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = False
    pygame.display.flip()

pygame.quit()
sys.exit()
