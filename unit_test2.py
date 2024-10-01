import math
import unittest
import SECOND_TOY_PROBLEM as sim

class TestParticleSimulation(unittest.TestCase):
    
    @staticmethod
    def calculate_theoretical_y(t, h, g):
        t1 = math.sqrt(2 * h / g)
        T = 2 * t1
        t_cycle = t % T

        if t_cycle <= t1:
            return h - 0.5 * g * t_cycle**2
        else:
            t_rising = t_cycle - t1
            v_initial = math.sqrt(2 * g * h)
            return v_initial * t_rising - 0.5 * g * t_rising**2

    def test_simulated_vs_theoretical_position(self):
        initial_height = 10.0
        initial_velocity = 0.0
        time_step = 0.05
        simulation_duration = 1.43
        g = 9.81
        spring_constant = 100.0

        particle = sim.Particle(0.0, initial_height, 0.0, -initial_velocity, 1.0, 1.0)
        box = sim.Box(50.0, 30.0, spring_constant)
        simulation = sim.Simulation(particle, box, time_step)

        for _ in range(int(simulation_duration / time_step)):
            position = simulation.runStep()
            print(f"Simulated Position: {position}")

        simulated_y_position = position[1]
        theoretical_y_position = self.calculate_theoretical_y(simulation_duration, initial_height, g)

        tolerance = 0.1
        self.assertTrue(math.isclose(simulated_y_position, theoretical_y_position, abs_tol=tolerance),
                        f"Simulated y ({simulated_y_position}) does not match theoretical y ({theoretical_y_position})")

        print(f"Test passed! Simulated y: {simulated_y_position}, Theoretical y: {theoretical_y_position}")

if __name__ == '__main__':
    unittest.main()
