import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import NINTH_TOY_PROBLEM as sim
import numpy as np

class ParticleSimulationVisualizer:
    def __init__(self, box_width=100.0, box_height=100.0, n_particles=25, 
                 spring_constant=10000.0, drop_height=20.0):
        self.first_collision_detected = False
        # Modified vibration parameters for more realistic behavior
        self.amplitude = 0.05  # Reduced to 0.5mm (more realistic for conveyor belts)
        self.frequency = 20.0  # Slightly reduced frequency
        self.particle_radius = 5.0  # Particle radius in mm
        
        # Initialize box with vibration parameters
        self.box = sim.Box(box_width, box_height, spring_constant, 
                          self.amplitude, self.frequency)
        
        # Store parameters
        self.n_particles = n_particles
        self.drop_height = drop_height
        self.max_height = 0.0
        
        # Generate particles with spacing
        self.particles = self._generate_particles()
        
        # Create simulation with smaller timestep for better accuracy
        self.time_step = 0.01  # 0.5ms timestep for better numerical stability
        self.simulation = sim.Simulation(self.particles, self.box, self.time_step)
        
        # Setup plotting
        self.fig, (self.ax_sim, self.ax_stats) = plt.subplots(1, 2, figsize=(15, 6))
        self._setup_plots()
        
        # Initialize data collection
        self.time_data = []
        self.height_data = []
        self.settled = False
        self.settling_threshold = 0.5  # mm of movement considered "settled"
        self.settling_time_threshold = 0.5  # seconds to consider particles settled
        self.last_positions = []
        self.stable_time = 0.0
        
    def _generate_particles(self):
        particles = []
        density = 2700.0  # kg/m³ (typical for rocks)
        
        # Fixed height for all particles
        fixed_y = self.drop_height
        
        for _ in range(self.n_particles):
            while True:  # Repeat until a valid position is found
                # Generate random particle radius in a realistic range (e.g., 3 to 10 mm)
                radius = np.random.uniform(1.0, 2.0)
                
                # Compute particle mass based on the volume and density
                mass = (4/3) * np.pi * radius**3 * density
                
                # Generate random initial x position within the box dimensions
                x_pos = np.random.uniform(radius, self.box.width - radius)  # Avoid placing at walls
                
                # Check if the new particle overlaps with existing particles
                no_overlap = True
                for existing_particle in particles:
                    distance = np.sqrt((x_pos - existing_particle.x)**2)
                    min_distance = radius + existing_particle.radius
                    if distance < min_distance:
                        no_overlap = False
                        break
                
                if no_overlap:
                    # Create a particle with positional arguments
                    particle = sim.Particle(
                        x_pos,  # x-coordinate
                        fixed_y,  # Fixed y-coordinate
                        np.random.uniform(-5.0, 5.0),  # vx: horizontal velocity
                        0.0,  # vy: vertical velocity
                        radius,  # Particle radius
                        mass  # Particle mass
                    )
                    particles.append(particle)
                    break  # Exit the loop when a valid particle is placed
        
        return particles




    
    def _setup_plots(self):
        # [Previous setup_plots code remains the same]
        # Setup simulation view
        self.ax_sim.set_xlim(0, self.box.width)
        self.ax_sim.set_ylim(0, self.box.height)
        self.ax_sim.set_aspect('equal')
        self.ax_sim.set_title(f'Conveyor Belt Simulation\nFreq: {self.frequency}Hz, Amp: {self.amplitude}units')
        
        # Setup statistics view
        self.ax_stats.set_xlim(0, 10)
        self.ax_stats.set_ylim(0, self.box.height)
        self.ax_stats.set_xlabel('Time (s)')
        self.ax_stats.set_ylabel('Height (units)')
        self.ax_stats.grid(True)
        
        # Create boundaries
        self.boundaries = []
        # Walls
        self.boundaries.extend([
            plt.Line2D([0, 0], [0, self.box.height], color='black', lw=2),
            plt.Line2D([self.box.width, self.box.width], [0, self.box.height], 
                      color='black', lw=2)
        ])
        # Vibrating bottom (conveyor belt)
        self.bottom = plt.Line2D([0, self.box.width], [0, 0], color='brown', lw=3)
        self.boundaries.append(self.bottom)
        
        for boundary in self.boundaries:
            self.ax_sim.add_line(boundary)
        
        # Create particle visualizations
        self.particles_vis = []
        self.rotation_markers = []
        
        for p in self.particles:
            # Use a more rock-like color
            circle = plt.Circle((p.x, p.y), p.radius, fc='gray', ec='darkgray', alpha=0.8)
            line = plt.Line2D([p.x, p.x + p.radius], 
                            [p.y, p.y], 
                            color='black', lw=1)
            
            self.ax_sim.add_patch(circle)
            self.ax_sim.add_line(line)
            
            self.particles_vis.append(circle)
            self.rotation_markers.append(line)
        
        # Height plot
        self.height_line, = self.ax_stats.plot([], [], 'b-', label='Average Height')
        self.max_height_line = self.ax_stats.axhline(y=0, color='r', linestyle='--', 
                                                    label='Max Height')
        self.drop_height_line = self.ax_stats.axhline(
        y=self.drop_height, color='g', linestyle=':', label='Drop Height'
    )
        self.ax_stats.legend()
    
    def check_settling(self, positions):
        if not self.last_positions:
            self.last_positions = positions
            return False
        
        max_movement = 0
        for curr, prev in zip(positions, self.last_positions):
            movement = np.sqrt((curr[0] - prev[0])**2 + (curr[1] - prev[1])**2)
            max_movement = max(max_movement, movement)
        
        self.last_positions = positions
        
        if max_movement < self.settling_threshold:
            self.stable_time += self.time_step
        else:
            self.stable_time = 0
            
        return self.stable_time >= self.settling_time_threshold
    
    def update(self, frame):
        # Run simulation step
        positions = self.simulation.runStep()
        
        # Update bottom boundary (conveyor belt)
        bottom_y = self.simulation.getCurrentBottomBoundaryPosition()
        self.bottom.set_ydata([bottom_y, bottom_y])
        
        # Track heights and update particles
        current_heights = []
        bottom_collided = False  # Flag to check bottom collision in this step
        
        for i, (circle, marker) in enumerate(zip(self.particles_vis, self.rotation_markers)):
            pos = positions[i]
            x, y, theta = pos[0], pos[1], pos[2]
            marker_x, marker_y = pos[3], pos[4]
            
            circle.center = (x, y)
            marker.set_data([x, marker_x], [y, marker_y])
            
            current_heights.append(y)
            
            # Detect collision with bottom wall
            if not self.first_collision_detected and y - self.particles[i].radius <= bottom_y:
                bottom_collided = True
        
        if bottom_collided:
            self.first_collision_detected = True
        
        # Calculate statistics
        avg_height = np.mean(current_heights)
        if self.first_collision_detected:
            self.max_height = max(self.max_height, max(current_heights))
        
        # Update plots
        self.time_data.append(frame * self.time_step)
        self.height_data.append(avg_height)
        
        self.height_line.set_data(self.time_data, self.height_data)
        if self.first_collision_detected:
            self.max_height_line.set_ydata([self.max_height, self.max_height])
        else:
            self.max_height_line.set_ydata([0, 0])  # Keep the line at 0 initially
        
        # Check if particles have settled
        if not self.settled and self.check_settling(positions):
            self.settled = True
            print(f"\nParticles settled at t = {frame * self.time_step:.2f}s")
        
        # Adjust plot limits
        self.ax_stats.set_xlim(0, max(10, frame * self.time_step))
        self.ax_stats.set_ylim(0, max(self.max_height * 1.1, self.box.height))
        
        return (self.boundaries + self.particles_vis + 
                self.rotation_markers + [self.height_line, self.max_height_line])
    def run(self, duration=10.0, interval=20):
        frames = int(duration / self.time_step)
        self.anim = FuncAnimation(
            self.fig, self.update,
            frames=frames,
            interval=interval,
            blit=True
        )
        plt.show()
        
        stats = self.simulation.getSimulationStats()
        print(f"\nSimulation Results:")
        print(f"Initial drop height: {self.drop_height:.2f} mm")
        print(f"Maximum bounce height: {stats.maxHeight:.2f} mm")
        print(f"Final settled height: {np.mean(self.height_data[-100:]):.2f} mm")
        return stats.maxHeight

# Example usage with modified parameters
if __name__ == "__main__":
    viz = ParticleSimulationVisualizer(
        box_width=100.0,
        box_height=100.0,
        n_particles=25,
        drop_height=20.0
    )
    max_height = viz.run(duration=10.0)