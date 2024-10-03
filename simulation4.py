import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import FOURTH_TOY_PROBLEM as sim

particle1 = sim.Particle(10.0, 25.0, 5.0, 0.0, 2.0, 1.0)  # x, y, vx, vy, radius, mass
particle2 = sim.Particle(30.0, 10.0, -5.0, 0.0, 2.0, 1.0)  # x, y, vx, vy, radius, mass

box = sim.Box(50.0, 30.0, 1000.0)  # width, height, springConstant

time_step = 0.01
simulation = sim.Simulation(particle1, particle2, box, time_step)

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, box.width)
ax.set_ylim(0, box.height)

box_patch = patches.Rectangle((0, 0), box.width, box.height, linewidth=1, edgecolor='black', facecolor='none')
ax.add_patch(box_patch)

particle_patch1 = plt.Circle((particle1.x, particle1.y), particle1.radius, color='red')
particle_patch2 = plt.Circle((particle2.x, particle2.y), particle2.radius, color='blue')
ax.add_patch(particle_patch1)
ax.add_patch(particle_patch2)

def update(frame):
    positions = simulation.runStep()
    particle_patch1.center = (positions[0][0], positions[0][1])
    particle_patch2.center = (positions[1][0], positions[1][1])
    return particle_patch1, particle_patch2

ani = FuncAnimation(fig, update, frames=500, interval=20, blit=True)

plt.title("Two-Particle Simulation with Hooke's Law")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.grid(True)
plt.show()
