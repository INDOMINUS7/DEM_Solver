import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import SIXTH_TOY_PROBLEM as sim
import random

# Set the number of particles (you can modify this value)
n = 10
 # Increased number for better visuals

# Function to generate a random float within a specified range
def random_float(low, high):
    return random.uniform(low, high)

# Generate 'n' random particles inside the box
def generate_random_particles(n, box_width, box_height):
    particles = []
    for _ in range(n):
        radius = random_float(1.5, 3.5)  # Random radius between 1.5 and 3.5 units for variation
        mass = (4/3) * 3.1415 * radius**3  # Calculating the mass based on radius (assuming uniform density)
        startX = random_float(radius + 2, box_width - radius - 2)  # Random x within safe box boundaries
        startY = random_float(radius + 2, box_height - radius - 2)  # Random y within safe box boundaries
        startVx = random_float(-5.0, 5.0)  # Reduced x velocity for smoother motion
        startVy = random_float(-5.0, 5.0)  # Reduced y velocity for smoother motion
        particle = sim.Particle(startX, startY, startVx, startVy, radius, mass)
        particles.append(particle)
    return particles

# Box dimensions and spring constant
box = sim.Box(100.0, 50.0, 100000.0)

# Generate 'n' random particles
particles = generate_random_particles(n, box.width, box.height)

# Time step for simulation
time_step = 0.01
simulation = sim.Simulation(particles, box, time_step)

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, box.width)
ax.set_ylim(0, box.height)

# Add the box boundary to the plot
box_patch = patches.Rectangle((0, 0), box.width, box.height, linewidth=1, edgecolor='black', facecolor='none')
ax.add_patch(box_patch)

# Generate distinct colors for each particle
colors = plt.cm.viridis([i / n for i in range(n)])

# Initialize the particle patches (circles) with distinct colors
# Removed the 'alpha' parameter to make particles non-transparent
particle_patches = [plt.Circle((p.x, p.y), p.radius, color=colors[i]) for i, p in enumerate(particles)]
for patch in particle_patches:
    ax.add_patch(patch)

# Function to update the particle positions in each frame
def update(frame):
    positions = simulation.runStep()
    for i, patch in enumerate(particle_patches):
        patch.center = (positions[i][0], positions[i][1])
    return particle_patches

# Function to stop the animation when it reaches the last frame
def stop_animation(event_source, num_frames):
    if event_source.frame_seq.__next__() >= num_frames:
        event_source.stop()

# Set total simulation time (e.g., 8 seconds for smoother animation)
total_simulation_time = 8.0  # in seconds
num_frames = int(total_simulation_time / time_step)  # Total number of frames based on the time_step

# Create the animation with the specified number of frames
ani = FuncAnimation(fig, update, frames=num_frames, interval=20, blit=True)

# Add the stop condition
ani._start()  # Start the event source before attaching the stop function
ani.event_source.add_callback(lambda: stop_animation(ani.event_source, num_frames))

plt.title(f"DEM Particle Simulation with {n} Particles")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.grid(True)

# Display the animation
plt.show()
