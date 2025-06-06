import os
import random
import ELEVENTH_TOY_PROBLEM as sim  # Updated module
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
num_particles = 1000000

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

# Measure time for running the simulation
tic = time.time()
execution_time = simulation.measureExecutionTime(num_steps)
toc = time.time()
taken = toc - tic
print(f"simulation.measure {taken =}")

# Print the execution time
print(f"Execution time for {num_particles} particles with updated code: {execution_time} seconds")