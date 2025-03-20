import os
import random
import sys
import TENTH_TOY_PROBLEM as sim
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

def main(num_threads):
    # Set the number of threads for OpenMP
    os.environ["OMP_NUM_THREADS"] = str(num_threads)
    
    # Generate particles
    num_particles = 10000  # Keep problem size constant
    particles = generate_random_particles(num_particles)
    
    # Initialize box and simulation
    box = sim.Box(box_width, box_height, 5000.0)
    time_step = 0.01
    simulation = sim.Simulation(particles, box, time_step)
    
    # Measure execution time
    num_steps = 10  # Number of simulation steps
    execution_time = simulation.measureExecutionTime(num_steps)
    
    print(f"Threads: {num_threads}, Execution Time: {execution_time} seconds")
    return execution_time

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <num_threads>")
        sys.exit(1)
    
    num_threads = int(sys.argv[1])
    main(num_threads)