import os
import random
import EIGHTH_TOY_PROBLEM as sim  # Updated module
import time

# Box dimensions
box_width = 50.0
box_height = 30.0

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

tic = time.time()
box = sim.Box(box_width, box_height, 5000.0)
toc = time.time()
taken = toc - tic
print(f"sim.Box {taken =}")

time_step = 0.01
num_particles = 1000000

tic = time.time()
particles = generate_random_particles(num_particles)
toc = time.time()
taken = toc - tic
print(f"generate particles {taken =}")

tic = time.time()
simulation = sim.Simulation(particles, box, time_step)
toc = time.time()
taken = toc - tic
print(f"sim.Simulation {taken =}")

num_steps = 1

tic = time.time()
execution_time = simulation.measureExecutionTime(num_steps)
toc = time.time()
taken = toc - tic
print(f"simulation.measure {taken =}")

print(f"Execution time for {num_particles} particles with old code: {execution_time} seconds")