import numpy as np
import matplotlib.pyplot as plt
from ELEVENTH_TOY_PROBLEM import Particle, Box, Simulation

def run_bne_simulation(width, height, frequency, amplitude, total_time=10.0):
    # Fixed parameters
    spring_constant = 10000.0
    dt = 0.001
    small_r = 0.04
    large_r = 0.12
    density = 1000.0
    
    # Initialize particles
    particles = []
    np.random.seed(42)
    for _ in range(60):
        x = np.random.uniform(small_r, width - small_r)
        y = np.random.uniform(0.2, 0.8)
        m = np.pi * small_r**2 * density
        particles.append(Particle(x, y, 0.0, 0.0, small_r, m))
    
    # Add large particle
    large_mass = np.pi * large_r**2 * density
    particles.append(Particle(width/2, 0.1, 0.0, 0.0, large_r, large_mass))
    
    # Run simulation
    sim = Simulation(particles, Box(width, height, spring_constant), dt)
    max_height = 0
    top_time = None
    
    for step in range(int(total_time/dt)):
        t = step * dt
        pseudo_acc = (2 * np.pi * frequency)**2 * amplitude * np.sin(2 * np.pi * frequency * t)
        for p in sim.particles:
            p.vy += pseudo_acc * dt
        
        pos = sim.runStep()
        current_height = pos[-1][1]  # y of large particle
        
        if current_height > max_height:
            max_height = current_height
        if current_height > height*0.9 and top_time is None:  # Reached top 90%
            top_time = t
            
    return max_height, top_time

# Test parameters
amplitudes = np.linspace(0.01, 0.2, 5)  # 0.01 to 0.1 m
frequencies = np.linspace(10, 50, 5)     # 1 to 20 Hz

# Fixed frequency, varying amplitude
fixed_freq = 30.0
max_heights_amp = []
print("Amplitude vs Max Height Data Points:")
print("Amplitude (m)\tMax Height (m)")
for amp in amplitudes:
    max_h, _ = run_bne_simulation(1.0, 1.5, fixed_freq, amp)
    max_heights_amp.append(max_h)
    print(f"{amp:.3f}\t\t{max_h:.3f}")

# Fixed amplitude, varying frequency
fixed_amp = 0.1
max_heights_freq = []
print("\nFrequency vs Max Height Data Points:")
print("Frequency (Hz)\tMax Height (m)")
for freq in frequencies:
    max_h, _ = run_bne_simulation(1.0, 1.5, freq, fixed_amp)
    max_heights_freq.append(max_h)
    print(f"{freq:.1f}\t\t{max_h:.3f}")

# Plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Left plot - Amplitude vs Max Height
ax1.plot(amplitudes, max_heights_amp, 'o-')
ax1.set_xlabel('Amplitude (m)')
ax1.set_ylabel('Max Height Reached (m)')
ax1.set_title(f'Fixed Frequency = {fixed_freq} Hz')

# Add data point labels to the left plot
for i, (amp, height) in enumerate(zip(amplitudes, max_heights_amp)):
    ax1.text(amp, height, f'({amp:.2f}, {height:.2f})', 
             ha='center', va='bottom', fontsize=8)

# Right plot - Frequency vs Max Height
ax2.plot(frequencies, max_heights_freq, 's-')
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Max Height Reached (m)')
ax2.set_title(f'Fixed Amplitude = {fixed_amp} m')

# Add data point labels to the right plot
for i, (freq, height) in enumerate(zip(frequencies, max_heights_freq)):
    ax2.text(freq, height, f'({freq:.1f}, {height:.2f})', 
             ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('amplitude_frequency_interaction.png')
plt.show()