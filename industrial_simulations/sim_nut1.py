import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from ELEVENTH_TOY_PROBLEM import Particle, Box, Simulation

# Simulation parameters
width, height = 1.0, 1.5
spring_constant = 10000.0
dt = 0.0005
total_time = 10.0
steps = int(total_time / dt)
frequency = 30.0
amplitude = 0.20

# Particle parameters
density_small = 1500.0
density_large = 800.0
small_r = 0.04
large_r = 0.20

def compute_mass(r, density):
    return np.pi * r**2 * density

# Create particles
particles = []
np.random.seed(42)
for _ in range(500):  # 100 small particles
    x = np.random.uniform(small_r, width - small_r)
    y = np.random.uniform(0.2, 0.8)
    m = compute_mass(small_r, density_small)
    particles.append(Particle(x, y, 0.0, 0.0, small_r, m))

# Add one large Brazil nut
large_x, large_y = width / 2, 0.1
large_mass = compute_mass(large_r, density_large)
large_particle = Particle(large_x, large_y, 0.0, 0.0, large_r, large_mass)
particles.append(large_particle)

# Initialize simulation
box = Box(width, height, spring_constant)
sim = Simulation(particles, box, dt)

# Set up visualization
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, width)
ax.set_ylim(0, height)
ax.set_aspect('equal')
ax.set_title('Brazil Nut Effect Simulation')
ax.set_xlabel('Width (m)')
ax.set_ylabel('Height (m)')

# Draw box boundaries
box_rect = plt.Rectangle((0, 0), width, height, fill=False, 
                         edgecolor='black', linewidth=2)
ax.add_patch(box_rect)

# Create particle artists
small_particles = ax.scatter([], [], s=small_r*2000, c='blue', 
                            alpha=0.7)
large_particle = ax.scatter([], [], s=large_r*2000, c='red', 
                          alpha=1.0)
ax.legend()

# Animation update function
def update(frame):
    t = frame * dt
    pseudo_acc = (2 * np.pi * frequency)**2 * amplitude * np.sin(2 * np.pi * frequency * t)
    
    for p in sim.particles:
        p.vy += pseudo_acc * dt

    positions = sim.runStep()
    
    # Update particle positions
    small_pos = np.array([(p.x, p.y) for p in sim.particles[:-1]])
    large_pos = np.array([(sim.particles[-1].x, sim.particles[-1].y)])
    
    small_particles.set_offsets(small_pos)
    large_particle.set_offsets(large_pos)
    
    # Update title with current time
    ax.set_title(f'Brazil Nut Effect - Time: {t:.2f}s')
    
    return small_particles, large_particle

# Create animation
ani = FuncAnimation(fig, update, frames=steps, interval=10, blit=True)
plt.tight_layout()
plt.show()