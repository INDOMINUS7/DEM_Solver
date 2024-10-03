import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import THIRD_TOY_PROBLEM as sim

particle = sim.Particle(10.0, 25.0, 10.0, 0.0, 2.0, 1.0, 1e6, 0.3)
box = sim.Box(50.0, 30.0, 1e6, 0.3)

time_step = 0.00001
simulation = sim.Simulation(particle, box, time_step)

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, box.width)
ax.set_ylim(0, box.height)

box_patch = patches.Rectangle((0, 0), box.width, box.height, linewidth=1, edgecolor='black', facecolor='none')
ax.add_patch(box_patch)

particle_patch = plt.Circle((particle.x, particle.y), particle.radius, color='red')
ax.add_patch(particle_patch)

def update(frame):
    pos = simulation.runStep()
    particle_patch.center = (pos[0], pos[1])
    return particle_patch,

ani = FuncAnimation(fig, update, frames=500, interval=20, blit=True)

plt.title("Particle Simulation with Hertzian Model (Soft Material)")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.grid(True)
plt.show()
