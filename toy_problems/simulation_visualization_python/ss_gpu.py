import os
import random
import Strongana as sim  # Updated module
import time

# Box dimensions
box_width = 200.0
box_height = 150.0

# Function to generate random particles
def generate_random_particles(num_particles):
    particles = []
    
    for _ in range(num_particles):
        x = random.uniform(0, box_width)
        y = random.uniform(0, box_height)
        vx = random.uniform(-5.0, 5.0)
        vy = random.uniform(-5.0, 5.0)
        radius = random.uniform(1.0, 3.0)
        mass = (4/3) * 3.1415 * radius**3
        particles.append(sim.Particle(x, y, vx, vy, radius, mass))
    
    return particles

# Measure time for creating the Box object
tic = time.time()
box = sim.Box(box_width, box_height, 5000.0)
toc = time.time()
taken = toc - tic
print(f"sim.Box {taken =}")

# Simulation parameters
time_step = 0.01
num_particles = 10000

# Measure time for generating random particles
tic = time.time()
particles = generate_random_particles(num_particles)
toc = time.time()
taken = toc - tic
print(f"generate particles {taken =}")

# Measure time for creating the Simulation object
tic = time.time()
simulation = sim.Simulation(particles, box, time_step)
toc = time.time()
taken = toc - tic
print(f"sim.Simulation {taken =}")

# Number of simulation steps
num_steps = 100  # Increase this for more accurate timing

# Vary the number of gangs, workers, and vector lengths for strong scaling analysis
# Vary the number of gangs, workers, and vector lengths for strong scaling analysis
gangs_list = [1, 2, 4, 8]
workers_list = [1, 2, 4]
vector_lengths_list = [32, 64, 128]

for num_gangs in gangs_list:
    for num_workers in workers_list:
        for vector_length in vector_lengths_list:
            print(f"Running with {num_gangs} gangs, {num_workers} workers, and {vector_length} vector length")
            tic = time.time()
            execution_time = simulation.measureExecutionTime(num_steps, num_gangs, num_workers, vector_length)
            toc = time.time()
            taken = toc - tic
            print(f"Execution time for {num_particles} particles with {num_gangs} gangs, {num_workers} workers, and {vector_length} vector length: {execution_time} seconds")