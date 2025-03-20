import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import FIFTH_TOY_PROBLEM as sim

r1 = 2.0
r2 = 3.0

m1 = (4/3) * 3.1415 * r1**3  # Calculating the mass based on radius (assuming uniform density)
m2 = (4/3) * 3.1415 * r2**3

# Create two particles, positioned for head-on collision
particles = [
    sim.Particle(15.0, 15.0, 10.0, 0.0, r1, m1),  
    sim.Particle(40.0, 15.0, -10.0, 0.0, r2, m2)
]

box = sim.Box(50.0, 30.0, 5000.0)

time_step = 0.01
simulation = sim.Simulation(particles, box, time_step)

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, box.width)
ax.set_ylim(0, box.height)

# Add the box boundary to the plot
box_patch = patches.Rectangle((0, 0), box.width, box.height, linewidth=1, edgecolor='black', facecolor='none')
ax.add_patch(box_patch)

# Initialize the particle patches (circles)
particle_patches = [plt.Circle((p.x, p.y), p.radius, color='red') for p in particles]
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

# Set total simulation time (e.g., 5 seconds)
total_simulation_time = 5.0  # in seconds
num_frames = int(total_simulation_time / time_step)  # Total number of frames based on the time_step

# Create the animation with the specified number of frames
ani = FuncAnimation(fig, update, frames=num_frames, interval=20, blit=True)

# Add the stop condition
ani._start()  # Start the event source before attaching the stop function
ani.event_source.add_callback(lambda: stop_animation(ani.event_source, num_frames))

plt.title("Head-On Collision with Same Density and Different Sizes")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.grid(True)

# Display the animation
plt.show()
