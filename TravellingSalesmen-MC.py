import pygame
import random
import math
import numpy as np
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Markov Chain - Traveling Salesman Problem")

# Constants for TSP
NUM_CITIES = 100
NUM_ITERATIONS = 1000
INITIAL_TEMPERATURE = 100.0
COOLING_RATE = 0.99
CONVERGENCE_THRESHOLD = 50  # Iterations without improvement before stopping

# Generate random cities
cities = [(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(NUM_CITIES)]
city_distances = [[math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) for x2, y2 in cities] for x1, y1 in cities]


# Calculate path distance
def path_distance(path):
    return sum(city_distances[path[i]][path[i + 1]] for i in range(len(path) - 1)) + city_distances[path[-1]][path[0]]


# Generate a random path
def generate_random_path():
    path = list(range(NUM_CITIES))
    random.shuffle(path)
    return path


# Simulated Annealing Markov Chain
def simulated_annealing():
    current_path = generate_random_path()
    best_path = current_path[:]
    current_distance = path_distance(current_path)
    best_distance = current_distance

    temperature = INITIAL_TEMPERATURE
    no_improvement_count = 0  # Track iterations without improvement

    for iteration in range(NUM_ITERATIONS):
        # Create a new candidate path by swapping two cities
        new_path = current_path[:]
        i, j = random.sample(range(NUM_CITIES), 2)
        new_path[i], new_path[j] = new_path[j], new_path[i]

        new_distance = path_distance(new_path)

        # Accept new path based on Metropolis criterion
        if new_distance < current_distance or random.random() < np.exp((current_distance - new_distance) / temperature):
            current_path = new_path
            current_distance = new_distance

            # Update best path found
            if new_distance < best_distance:
                best_path = new_path
                best_distance = new_distance
                no_improvement_count = 0  # Reset the counter if we improve
            else:
                no_improvement_count += 1  # Increment if no improvement

        # Cool down the temperature
        temperature *= COOLING_RATE

        # Stop if we have not improved for a while
        if no_improvement_count >= CONVERGENCE_THRESHOLD:
            break

        # Return current iteration and best path for display
        yield best_path, best_distance, iteration


# Main loop
best_path = []
best_distance = float('inf')
running = True
simulated_annealing_gen = simulated_annealing()  # Create generator for simulated annealing
current_iteration = 0

while running:
    try:
        best_path, best_distance, current_iteration = next(simulated_annealing_gen)  # Get the next iteration
    except StopIteration:
        # If the generator is exhausted (finished), we can stop running
        running = False

    # Pygame visualization
    screen.fill(WHITE)

    # Draw cities
    for city in cities:
        pygame.draw.circle(screen, BLUE, city, 5)

    # Draw current best path
    if best_path:
        for i in range(len(best_path) - 1):
            pygame.draw.line(screen, RED, cities[best_path[i]], cities[best_path[i + 1]], 2)
        pygame.draw.line(screen, RED, cities[best_path[-1]], cities[best_path[0]], 2)  # Close the loop

    # Display shortest distance and current iteration
    font = pygame.font.SysFont(None, 30)
    distance_text = font.render(f"Shortest Distance: {best_distance:.2f}", True, BLACK)
    iteration_text = font.render(f"Current Iteration: {current_iteration}", True, BLACK)
    screen.blit(distance_text, (20, 20))
    screen.blit(iteration_text, (20, 50))

    pygame.display.flip()

    # Handle events to keep the window responsive
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
