import numpy as np
import matplotlib.pyplot as plt
from ELEVENTH_TOY_PROBLEM import Particle, Box, Simulation

# Constants
width, height = 1.0, 1.5
spring_constant = 10000.0
dt = 0.0005
total_time = 20.0
steps = int(total_time / dt)
density_small = 1500.0
density_large = 800.0
small_r = 0.04
large_r = 0.12
top_threshold = 0.8 * height  # 80% of container height

def compute_mass(r, density):
    return np.pi * r**2 * density

def run_simulation(frequency, amplitude):
    """Run simulation and return time to reach top threshold"""
    particles = []
    np.random.seed(42)
    for _ in range(80):
        x = np.random.uniform(small_r, width - small_r)
        y = np.random.uniform(0.2, 0.8)
        m = compute_mass(small_r, density_small)
        particles.append(Particle(x, y, 0.0, 0.0, small_r, m))
    
    large_mass = compute_mass(large_r, density_large)
    particles.append(Particle(width/2, 0.1, 0.0, 0.0, large_r, large_mass))
    
    box = Box(width, height, spring_constant)
    sim = Simulation(particles, box, dt)
    
    for step in range(steps):
        t = step * dt
        # Correct pseudo-force implementation (applies to all particles)
        pseudo_acc = (2 * np.pi * frequency)**2 * amplitude * np.sin(2 * np.pi * frequency * t)
        for p in sim.particles:
            p.vy += pseudo_acc * dt
        
        pos = sim.runStep()
        current_height = pos[-1][1]  # y of large particle
        
        if current_height >= top_threshold:
            return t  # Return time when threshold is reached
    
    return total_time  # If not reached within simulation time

# Generate data for amplitude variation (fixed frequency)
fixed_freq = 20.0
amplitudes = np.linspace(0.05, 0.20, 10)
times_amplitude = [run_simulation(fixed_freq, a) for a in amplitudes]

# Print amplitude variation data
print("Amplitude vs Time Data Points:")
print("Amplitude (m)\tTime to Reach Top (s)")
for amp, time in zip(amplitudes, times_amplitude):
    print(f"{amp:.3f}\t\t{time:.3f}")

# Generate data for frequency variation (fixed amplitude)
fixed_amp = 0.15
frequencies = np.linspace(10.0, 20.0, 10)
times_frequency = [run_simulation(f, fixed_amp) for f in frequencies]

# Print frequency variation data
print("\nFrequency vs Time Data Points:")
print("Frequency (Hz)\tTime to Reach Top (s)")
for freq, time in zip(frequencies, times_frequency):
    print(f"{freq:.1f}\t\t{time:.3f}")

# Plotting
plt.figure(figsize=(14, 6))

# Amplitude variation plot
plt.subplot(1, 2, 1)
plt.plot(amplitudes, times_amplitude, 'bo-', markersize=6)
plt.xlabel("Amplitude (m)", fontsize=11)
plt.ylabel("Time to reach top (s)", fontsize=11)
plt.title(f"Time to Reach Top vs Amplitude\n(Fixed Frequency = {fixed_freq} Hz)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# Add data labels to amplitude plot
for amp, time in zip(amplitudes, times_amplitude):
    plt.text(amp, time, f'({amp:.2f}, {time:.2f})', 
             ha='center', va='bottom', fontsize=9, color='blue')

# Frequency variation plot
plt.subplot(1, 2, 2)
plt.plot(frequencies, times_frequency, 'ro-', markersize=6)
plt.xlabel("Frequency (Hz)", fontsize=11)
plt.ylabel("Time to reach top (s)", fontsize=11)
plt.title(f"Time to Reach Top vs Frequency\n(Fixed Amplitude = {fixed_amp} m)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# Add data labels to frequency plot
for freq, time in zip(frequencies, times_frequency):
    plt.text(freq, time, f'({freq:.1f}, {time:.2f})', 
             ha='center', va='bottom', fontsize=9, color='red')

plt.tight_layout()
plt.show()