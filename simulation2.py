import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import SECOND_TOY_PROBLEM as sim  # Import the C++ code compiled as a Python module

# Initialize the Particle and Box (adding the mass parameter)
particle = sim.Particle(10.0, 25.0, 5.0, 0.0, 2.0, 1.0)  # x, y, vx, vy, radius, mass
box = sim.Box(50.0, 30.0, 1000.0)  # width, height, springConstant

# Time step for the simulation
time_step = 0.01

# Initialize the simulation
simulation = sim.Simulation(particle, box, time_step)

# Set up the figure and axis for animation
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, box.width)
ax.set_ylim(0, box.height)

# Add a rectangle to represent the box boundaries
box_patch = patches.Rectangle((0, 0), box.width, box.height, linewidth=1, edgecolor='black', facecolor='none')
ax.add_patch(box_patch)

# Add a circle to represent the particle
particle_patch = plt.Circle((particle.x, particle.y), particle.radius, color='red')
ax.add_patch(particle_patch)

# Update function for the animation
def update(frame):
    # Run a simulation step
    pos = simulation.runStep()
    # Update the position of the particle
    particle_patch.center = (pos[0], pos[1])
    return particle_patch,

# Create the animation
ani = FuncAnimation(fig, update, frames=500, interval=20, blit=True)

# Show the animation
plt.title("Real-Time Particle Simulation with Contact Forces")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.grid(True)
plt.show()
