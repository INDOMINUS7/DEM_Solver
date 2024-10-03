import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import FIFTH_TOY_PROBLEM as sim

# Create multiple particles
particles = [
    sim.Particle(10.0, 15.0, 2.0, 1.0, 1.0, 1.0),  # Particle 1
    sim.Particle(20.0, 25.0, -2.0, 1.5, 2.0, 1.0),  # Particle 2
    sim.Particle(30.0, 10.0, -1.0, -1.0, 1.0, 1.0),  # Particle 3
    sim.Particle(35.0, 12.0, 1.0, -1.0, 4.0, 1.0),  # Particle 4
    sim.Particle(25.0, 20.0, 2.0, -0.5, 2.0, 1.0),  # Particle 5
    sim.Particle(40.0, 18.0, -1.0, 1.0, 5.0, 1.0),  # Particle 6
    sim.Particle(18.0, 22.0, -1.0, 0.5, 2.0, 1.0),  # Particle 7
    sim.Particle(45.0, 28.0, 0.0, 0.0, 3.0, 1.0)   # Particle 8
]


# Box dimensions and spring constant
box = sim.Box(50.0, 30.0, 1000.0)

# Simulation parameters
time_step = 0.01
simulation = sim.Simulation(particles, box, time_step)

# Visualization setup
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, box.width)
ax.set_ylim(0, box.height)

# Draw box boundaries
box_patch = patches.Rectangle((0, 0), box.width, box.height, linewidth=1, edgecolor='black', facecolor='none')
ax.add_patch(box_patch)

# Create particle circles
particle_patches = [plt.Circle((p.x, p.y), p.radius, color='red') for p in particles]
for patch in particle_patches:
    ax.add_patch(patch)

def update(frame):
    positions = simulation.runStep()
    for i, patch in enumerate(particle_patches):
        patch.center = (positions[i][0], positions[i][1])
    return particle_patches

# Animation
ani = FuncAnimation(fig, update, frames=500, interval=20, blit=True)

plt.title("Particle Simulation with Hooke's Law (n particles)")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.grid(True)
plt.show()
