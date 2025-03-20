import matplotlib.pyplot as plt
import matplotlib.animation as animation  # Import FuncAnimation
import numpy as np
import NINTH_TOY_PROBLEM as sim

class ParticleSimulationVisualizer:
    def __init__(self, box_width=100.0, box_height=100.0, n_particles=25, 
                 spring_constant=10000.0, drop_height=10.0, amplitude=0.1, frequency=10.0):
        self.first_collision_detected = False
        self.amplitude = amplitude
        self.frequency = frequency
        self.particle_radius = 5.0
        
        self.box = sim.Box(box_width, box_height, spring_constant, 
                          self.amplitude, self.frequency)
        
        self.n_particles = n_particles
        self.drop_height = drop_height
        self.max_height = 0.0
        
        self.particles = self._generate_particles()
        
        self.time_step = 0.01
        self.simulation = sim.Simulation(self.particles, self.box, self.time_step)
        
        self.fig, (self.ax_sim, self.ax_stats) = plt.subplots(1, 2, figsize=(15, 6))
        self._setup_plots()
        
        self.time_data = []
        self.height_data = []
        self.settled = False
        self.settling_threshold = 0.5
        self.settling_time_threshold = 0.5
        self.last_positions = []
        self.stable_time = 0.0
        
    def _generate_particles(self):
        particles = []
        density = 2700.0
        
        fixed_y = self.drop_height
        
        for _ in range(self.n_particles):
            while True:
                radius = np.random.uniform(1.0, 2.0)
                mass = (4/3) * np.pi * radius**3 * density
                x_pos = np.random.uniform(radius, self.box.width - radius)
                
                no_overlap = True
                for existing_particle in particles:
                    distance = np.sqrt((x_pos - existing_particle.x)**2)
                    min_distance = radius + existing_particle.radius
                    if distance < min_distance:
                        no_overlap = False
                        break
                
                if no_overlap:
                    particle = sim.Particle(
                        x_pos, fixed_y, np.random.uniform(-5.0, 5.0), 0.0, radius, mass
                    )
                    particles.append(particle)
                    break
        
        return particles
    
    def _setup_plots(self):
        self.ax_sim.set_xlim(0, self.box.width)
        self.ax_sim.set_ylim(0, self.box.height)
        self.ax_sim.set_aspect('equal')
        self.ax_sim.set_title(f'Conveyor Belt Simulation\nFreq: {self.frequency}Hz, Amp: {self.amplitude}units')
        
        self.ax_stats.set_xlim(0, 10)
        self.ax_stats.set_ylim(0, self.box.height)
        self.ax_stats.set_xlabel('Time (s)')
        self.ax_stats.set_ylabel('Height (units)')
        self.ax_stats.grid(True)
        
        self.boundaries = [
            plt.Line2D([0, 0], [0, self.box.height], color='black', lw=2),
            plt.Line2D([self.box.width, self.box.width], [0, self.box.height], color='black', lw=2)
        ]
        self.bottom = plt.Line2D([0, self.box.width], [0, 0], color='brown', lw=3)
        self.boundaries.append(self.bottom)
        
        for boundary in self.boundaries:
            self.ax_sim.add_line(boundary)
        
        self.particles_vis = []
        self.rotation_markers = []
        
        for p in self.particles:
            circle = plt.Circle((p.x, p.y), p.radius, fc='gray', ec='darkgray', alpha=0.8)
            line = plt.Line2D([p.x, p.x + p.radius], [p.y, p.y], color='black', lw=1)
            
            self.ax_sim.add_patch(circle)
            self.ax_sim.add_line(line)
            
            self.particles_vis.append(circle)
            self.rotation_markers.append(line)
        
        self.height_line, = self.ax_stats.plot([], [], 'b-', label='Average Height')
        self.max_height_line = self.ax_stats.axhline(y=0, color='r', linestyle='--', label='Max Height')
        self.drop_height_line = self.ax_stats.axhline(y=self.drop_height, color='g', linestyle=':', label='Drop Height')
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
        positions = self.simulation.runStep()
        bottom_y = self.simulation.getCurrentBottomBoundaryPosition()
        self.bottom.set_ydata([bottom_y, bottom_y])
        
        current_heights = []
        bottom_collided = False
        
        for i, (circle, marker) in enumerate(zip(self.particles_vis, self.rotation_markers)):
            pos = positions[i]
            x, y, theta = pos[0], pos[1], pos[2]
            marker_x, marker_y = pos[3], pos[4]
            
            circle.center = (x, y)
            marker.set_data([x, marker_x], [y, marker_y])
            
            current_heights.append(y)
            
            if not self.first_collision_detected and y - self.particles[i].radius <= bottom_y:
                bottom_collided = True
        
        if bottom_collided:
            self.first_collision_detected = True
        
        avg_height = np.mean(current_heights)
        if self.first_collision_detected:
            self.max_height = max(self.max_height, max(current_heights))
        
        self.time_data.append(frame * self.time_step)
        self.height_data.append(avg_height)
        
        self.height_line.set_data(self.time_data, self.height_data)
        if self.first_collision_detected:
            self.max_height_line.set_ydata([self.max_height, self.max_height])
        else:
            self.max_height_line.set_ydata([0, 0])
        
        if not self.settled and self.check_settling(positions):
            self.settled = True
            print(f"\nParticles settled at t = {frame * self.time_step:.2f}s")
        
        self.ax_stats.set_xlim(0, max(10, frame * self.time_step))
        self.ax_stats.set_ylim(0, max(self.max_height * 1.1, self.box.height))
        
        return (self.boundaries + self.particles_vis + 
                self.rotation_markers + [self.height_line, self.max_height_line])
    
    def run(self, duration=10.0, interval=20):
        frames = int(duration / self.time_step)
        self.anim = animation.FuncAnimation(  # Use animation.FuncAnimation
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

def run_simulation_for_frequency_and_amplitude(frequency, amplitude):
    viz = ParticleSimulationVisualizer(
        box_width=100.0,
        box_height=100.0,
        n_particles=25,
        drop_height=30.0,
        amplitude=amplitude,
        frequency=frequency
    )
    max_height = viz.run(duration=20.0)
    return max_height

def main():
    frequencies = [10, 20, 30]
    amplitudes = np.arange(0, 0.1, 0.02)
    
    results = {freq: [] for freq in frequencies}
    
    for freq in frequencies:
        for amp in amplitudes:
            max_height = run_simulation_for_frequency_and_amplitude(freq, amp)
            results[freq].append(max_height)
    
    # Plotting the results
    plt.figure(figsize=(10, 6))
    for freq in frequencies:
        plt.plot(amplitudes, results[freq], label=f'{freq} Hz')
    
    plt.xlabel('Amplitude (units)')
    plt.ylabel('Maximum Height (units)')
    plt.title('Maximum Height vs Amplitude for Different Frequencies')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()