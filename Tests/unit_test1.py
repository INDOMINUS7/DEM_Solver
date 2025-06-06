import math
import unittest
import FIRST_TOY_PROBLEM as sim  # Import your first toy problem for the hard sphere model

class TestParticleSimulation(unittest.TestCase):
    
    @staticmethod
    def calculate_theoretical_y(t, h, g):
        """
        Calculate the theoretical y position of a particle with perfect elasticity
        after time t, starting from height h and under gravity g.
        """
        # Calculate t1 (time to hit the ground for the first time)
        t1 = math.sqrt(2 * h / g)
        
        # Calculate the period of motion (one complete fall + bounce cycle)
        T = 2 * t1

        # Calculate time within the current cycle
        t_cycle = t % T

        # If within the falling phase (first half of the cycle)
        if t_cycle <= t1:
            # Use the equation for the falling phase
            return h - 0.5 * g * t_cycle**2
        else:
            # Use the equation for the rising phase (second half of the cycle)
            t_rising = t_cycle - t1
            
            # Calculate the initial velocity after the bounce
            v_initial = math.sqrt(2 * g * h)
            
            # Calculate the height during the rising phase
            return v_initial * t_rising - 0.5 * g * t_rising**2

    def test_simulated_vs_theoretical_position(self):
        initial_height = 10.0  # Initial height (m)
        initial_velocity = 0.0  # Set this to a small negative value for a downward motion
        time_step = 0.05  # Time step for simulation (s)
        simulation_duration = 4  # Total time to simulate (s)
        g = 9.81  # Gravity (m/s^2)

        # Create the particle and box
        particle = sim.Particle(0.0, initial_height, 0.0, -initial_velocity, 1.0)  # Start with negative velocity to fall
        box = sim.Box(50.0, 30.0)
        simulation = sim.Simulation(particle, box, time_step)

        # Run the simulation for the desired duration
        for _ in range(int(simulation_duration / time_step)):
            position = simulation.runStep()  # This will give you the updated position
            print(f"Simulated Position: {position}")  # Print to see the position updates

        # Get the simulated y position after simulation duration
        simulated_y_position = position[1]  # Use the position from runStep

        # Calculate the theoretical y position using the given formula
        theoretical_y_position = self.calculate_theoretical_y(simulation_duration, initial_height, g)

        # Tolerance for floating-point comparison
        tolerance = 0.1

        # Check if the simulated y-position matches the theoretical y-position within a given tolerance
        self.assertTrue(math.isclose(simulated_y_position, theoretical_y_position, abs_tol=tolerance),
                        f"Simulated y ({simulated_y_position}) does not match theoretical y ({theoretical_y_position})")

        print(f"Test passed! Simulated y: {simulated_y_position}, Theoretical y: {theoretical_y_position}")


if __name__ == '__main__':
    unittest.main()
