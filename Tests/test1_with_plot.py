import math
import unittest
import matplotlib.pyplot as plt
import FIRST_TOY_PROBLEM as sim

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
        initial_height = 15.0
        initial_velocity = 0.0
        time_step = 0.001
        simulation_duration = 4
        g = 9.81

        times = []
        simulated_y_positions = []
        theoretical_y_positions = []

        particle = sim.Particle(0.0, initial_height, 0.0, -initial_velocity, 1.0)
        box = sim.Box(50.0, 30.0)
        simulation = sim.Simulation(particle, box, time_step)

        for i in range(int(simulation_duration / time_step)):
            time = i * time_step
            position = simulation.runStep()

            times.append(time)
            simulated_y_positions.append(position[1])
            theoretical_y_positions.append(self.calculate_theoretical_y(time, initial_height, g))

        plt.plot(times, simulated_y_positions, label="Simulated y-Position")
        plt.plot(times, theoretical_y_positions, label="Theoretical y-Position", linestyle="--")

        plt.title("Simulated vs Theoretical Y Position")
        plt.xlabel("Time (s)")
        plt.ylabel("Y Position (m)")
        plt.legend()
        plt.grid(True)
        plt.show()

        tolerance = 0.1
        final_simulated_y = simulated_y_positions[-1]
        final_theoretical_y = theoretical_y_positions[-1]
        self.assertTrue(math.isclose(final_simulated_y, final_theoretical_y, abs_tol=tolerance),
                        f"Simulated y ({final_simulated_y}) does not match theoretical y ({final_theoretical_y})")

        print(f"Test passed! Final Simulated y: {final_simulated_y}, Final Theoretical y: {final_theoretical_y}")

if __name__ == '__main__':
    unittest.main()
