import matplotlib.pyplot as plt
import time
import numpy as np
import NINTH_TOY_PROBLEM as sim

class ParticleSimulationPerformanceTester:
    def __init__(self, box_width=100.0, box_height=100.0, 
                 spring_constant=10000.0, drop_height=10.0):
        """
        Initialize performance tester with configurable simulation parameters
        
        Args:
            box_width (float): Width of the simulation container
            box_height (float): Height of the simulation container
            spring_constant (float): Spring constant for wall interactions
            drop_height (float): Initial height from which particles are dropped
        """
        self.box_width = box_width
        self.box_height = box_height
        self.spring_constant = spring_constant
        self.drop_height = drop_height
        
    def _generate_particles(self, n_particles):
        """
        Generate a list of particles with random initial conditions
        
        Args:
            n_particles (int): Number of particles to generate
        
        Returns:
            list: List of Particle objects
        """
        particles = []
        density = 2700.0  # kg/m³ (typical for rocks)
        
        for _ in range(n_particles):
            while True:
                radius = np.random.uniform(1.0, 2.0)
                mass = (4/3) * np.pi * radius**3 * density
                x_pos = np.random.uniform(radius, self.box_width - radius)
                
                # Check for overlap
                no_overlap = all(
                    np.sqrt((x_pos - p.x)**2) >= (radius + p.radius) 
                    for p in particles
                )
                
                if no_overlap:
                    particle = sim.Particle(
                        x_pos,  # x-coordinate
                        self.drop_height,  # Fixed y-coordinate
                        np.random.uniform(-5.0, 5.0),  # vx
                        0.0,  # vy
                        radius,  # Particle radius
                        mass  # Particle mass
                    )
                    particles.append(particle)
                    break
        
        return particles
    
    def run_performance_test(self, particle_counts, simulation_duration=5.0):
        """
        Run performance tests for different particle counts
        
        Args:
            particle_counts (list): List of particle counts to test
            simulation_duration (float): Duration of each simulation
        
        Returns:
            dict: Performance results with particle counts and execution times
        """
        results = {
            'particle_counts': [],
            'execution_times': [],
            'avg_step_times': []
        }
        
        for n_particles in particle_counts:
            print(f"\nTesting {n_particles} particles...")
            
            # Generate particles
            particles = self._generate_particles(n_particles)
            
            # Create box with vibration parameters
            box = sim.Box(self.box_width, self.box_height, self.spring_constant, 0.05, 20.0)

            
            # Create simulation
            time_step = 0.01  # 10ms timestep
            simulation = sim.Simulation(particles, box, time_step)
            
            # Timing the entire simulation
            start_time = time.time()
            
            # Track step times
            step_times = []
            
            # Run simulation steps
            total_steps = int(simulation_duration / time_step)
            for _ in range(total_steps):
                step_start = time.time()
                simulation.runStep()
                step_time = time.time() - step_start
                step_times.append(step_time)
            
            total_time = time.time() - start_time
            
            # Store results
            results['particle_counts'].append(n_particles)
            results['execution_times'].append(total_time)
            results['avg_step_times'].append(np.mean(step_times))
            
            print(f"Total Execution Time: {total_time:.4f} seconds")
            print(f"Average Step Time: {np.mean(step_times):.6f} seconds")
        
        return results
    
    def plot_performance_results(self, results):
        """
        Plot performance results
        
        Args:
            results (dict): Performance test results
        """
        plt.figure(figsize=(12, 5))
        
        # Total Execution Time Plot
        plt.subplot(1, 2, 1)
        plt.plot(results['particle_counts'], results['execution_times'], marker='o')
        plt.title('Total Execution Time')
        plt.xlabel('Number of Particles')
        plt.ylabel('Execution Time (seconds)')
        plt.xscale('log')
        plt.grid(True)
        
        # Average Step Time Plot
        plt.subplot(1, 2, 2)
        plt.plot(results['particle_counts'], results['avg_step_times'], marker='o', color='green')
        plt.title('Average Step Execution Time')
        plt.xlabel('Number of Particles')
        plt.ylabel('Average Step Time (seconds)')
        plt.xscale('log')
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
        
        return results

# Example usage
if __name__ == "__main__":
    # Define a range of particle counts with logarithmic spacing
    particle_counts = [10, 25, 50, 100, 250, 500, 1000]
    
    # Initialize performance tester
    tester = ParticleSimulationPerformanceTester()
    
    # Run performance tests
    results = tester.run_performance_test(particle_counts)
    
    # Plot results
    tester.plot_performance_results(results)