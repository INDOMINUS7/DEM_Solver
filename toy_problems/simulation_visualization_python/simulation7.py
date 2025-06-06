import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import SEVENTH_TOY_PROBLEM as sim
import random
import numpy as np

class ParticleSimulationVisualizer:
    def __init__(self, box_width=100.0, box_height=50.0, n_particles=10, spring_constant=100000.0):
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
            # Larger variation in particle sizes
            radius = self.random_float(1.5, 4.0)
            # Density-based mass calculation (assuming density = 1)
            mass = (4/3) * np.pi * radius**3
            
            # Ensure particles are well-distributed and not overlapping
            while True:
                startX = self.random_float(radius + 2, self.box.width - radius - 2)
                startY = self.random_float(radius + 2, self.box.height - radius - 2)
                
                # Check for overlap with existing particles
                overlap = False
                for p in particles:
                    dx = startX - p.x
                    dy = startY - p.y
                    dist = np.sqrt(dx*dx + dy*dy)
                    if dist < (radius + p.radius + 1):  # +1 for safety margin
                        overlap = True
                        break
                
                if not overlap:
                    break
            
            # Randomize initial velocities
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
        
        # Create particle patches with different colors based on mass
        masses = [p.mass for p in self.particles]
        normalized_masses = [(m - min(masses)) / (max(masses) - min(masses)) for m in masses]
        colors = plt.cm.viridis(normalized_masses)
        
        self.particle_patches = [
            plt.Circle((p.x, p.y), p.radius, color=colors[i], alpha=0.7)
            for i, p in enumerate(self.particles)
        ]
        
        for patch in self.particle_patches:
            self.ax.add_patch(patch)
        
        # Add grid and labels
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.title(f"DEM Particle Simulation with Damping and Friction ({self.n_particles} Particles)")
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        
        # Make plot aspect ratio equal for better visualization
        self.ax.set_aspect('equal')
        
    def update(self, frame):
        positions = self.simulation.runStep()
        for i, patch in enumerate(self.particle_patches):
            patch.center = (positions[i][0], positions[i][1])
        return self.particle_patches
    
    def run_animation(self, duration=8.0, interval=20):
        self.setup_animation()
        num_frames = int(duration / self.time_step)
        self.animation = FuncAnimation(
            self.fig, self.update,
            frames=num_frames,
            interval=interval,
            blit=True
        )
        plt.show()

# Usage example
if __name__ == "__main__":
    visualizer = ParticleSimulationVisualizer(
        box_width=100.0,
        box_height=50.0,
        n_particles=35
    )
    visualizer.run_animation(duration=8.0)