import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import EIGHTH_TOY_PROBLEM as sim
import random
import numpy as np
import time

class ParticleSimulationVisualizer:
    def __init__(self, box_width=100.0, box_height=50.0, n_particles=1000, spring_constant=100000.0):
        self.box = sim.Box(box_width, box_height, spring_constant)
        self.n_particles = n_particles
        self.particles = self.generate_random_particles()
        self.time_step = 0.01
        self.simulation = sim.Simulation(self.particles, self.box, self.time_step)
        
    def random_float(self, low, high):
        return random.uniform(low, high)
    
    def generate_random_particles(self):
        particles = []
        for _ in range(self.n_particles):
            radius = self.random_float(1.5, 4.0)
            mass = (4/3) * np.pi * radius**3
            
            while True:
                startX = self.random_float(radius + 2, self.box.width - radius - 2)
                startY = self.random_float(radius + 2, self.box.height - radius - 2)
                
                overlap = False
                for p in particles:
                    dx = startX - p.x
                    dy = startY - p.y
                    dist = np.sqrt(dx*dx + dy*dy)
                    if dist < (radius + p.radius + 1):
                        overlap = True
                        break
                
                if not overlap:
                    break
            
            startVx = self.random_float(-15.0, 15.0)
            startVy = self.random_float(-15.0, 15.0)
            
            particle = sim.Particle(startX, startY, startVx, startVy, radius, mass)
            particles.append(particle)
        return particles
    
    def setup_animation(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_xlim(0, self.box.width)
        self.ax.set_ylim(0, self.box.height)
        
        # Add box boundary
        box_patch = patches.Rectangle((0, 0), self.box.width, self.box.height,
                                    linewidth=2, edgecolor='black', facecolor='none')
        self.ax.add_patch(box_patch)
        
        # Create particle patches and rotation markers
        masses = [p.mass for p in self.particles]
        normalized_masses = [(m - min(masses)) / (max(masses) - min(masses)) for m in masses]
        colors = plt.cm.viridis(normalized_masses)
        
        self.particle_patches = []
        self.rotation_lines = []
        
        for i, p in enumerate(self.particles):
            # Create circle patch for particle
            circle = plt.Circle((p.x, p.y), p.radius, color=colors[i], alpha=0.7)
            self.particle_patches.append(circle)
            self.ax.add_patch(circle)
            
            # Create line for rotation visualization
            line = plt.Line2D([p.x, p.x], [p.y, p.y], color='red', linewidth=2)
            self.rotation_lines.append(line)
            self.ax.add_line(line)
        
        # Add grid and labels
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.title(f"DEM Particle Simulation with Rotation added ({self.n_particles} Particles)")
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        
        self.ax.set_aspect('equal')
        
    def update(self, frame):
        # Unpack positions from the returned pair
        positions, _ = self.simulation.runStep()  # Ignore velocities

        all_artists = []
        
        for i, (patch, line) in enumerate(zip(self.particle_patches, self.rotation_lines)):
            # Update particle position (center of circle)
            center_x, center_y = positions[i][0], positions[i][1]
            patch.center = (center_x, center_y)
            
            # Update rotation line
            marker_x, marker_y = positions[i][3], positions[i][4]  # Get marker endpoint
            line.set_xdata([center_x, marker_x])
            line.set_ydata([center_y, marker_y])
            
            all_artists.append(patch)
            all_artists.append(line)
            
        return all_artists
    
    def run_animation(self, duration=8.0, interval=20):
        self.setup_animation()
        num_frames = int(duration / self.time_step)

        # Start timing
        start_time = time.time()

        def timed_update(frame):
            return self.update(frame)
        
        self.animation = FuncAnimation(
            self.fig, timed_update,
            frames=num_frames,
            interval=interval,
            blit=True
        )

        # End timing
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_step = total_time / num_frames
        print(f"Total simulation time: {total_time:.2f} seconds")
        print(f"Average time per step: {avg_time_per_step:.4f} seconds")

        plt.show()
# Usage example
if __name__ == "__main__":
    visualizer = ParticleSimulationVisualizer(
        box_width=100.0,
        box_height=50.0,
        n_particles=45
    )
    visualizer.run_animation(duration=8.0)
