import numpy as np
import matplotlib.pyplot as plt
from ELEVENTH_TOY_PROBLEM import Particle, Box, Simulation

def run_size_ratio_simulation(size_ratio, amplitude=0.1, frequency=15.0, total_time=10.0):
    # Fixed parameters
    width, height = 1.0, 1.5
    spring_constant = 10000.0
    dt = 0.001
    small_r = 0.04
    density = 1000.0
    
    # Calculate large particle size
    large_r = small_r * size_ratio
    
    # Initialize particles (60 small + 1 large)
    particles = []
    np.random.seed(42)  # For reproducibility
    for _ in range(60):
        x = np.random.uniform(small_r, width - small_r)
        y = np.random.uniform(0.2, 0.8)
        m = np.pi * small_r**2 * density
        particles.append(Particle(x, y, 0.0, 0.0, small_r, m))
    
    # Add large particle (start near bottom)
    large_mass = np.pi * large_r**2 * density
    particles.append(Particle(width/2, large_r + 0.05, 0.0, 0.0, large_r, large_mass))
    
    # Run simulation
    sim = Simulation(particles, Box(width, height, spring_constant), dt)
    max_height = 0
    
    for _ in range(int(total_time/dt)):
        t = _ * dt
        pseudo_acc = (2 * np.pi * frequency)**2 * amplitude * np.sin(2 * np.pi * frequency * t)
        for p in sim.particles:
            p.vy += pseudo_acc * dt
        
        pos = sim.runStep()
        current_height = pos[-1][1]  # y of large particle
        max_height = max(max_height, current_height)
            
    return max_height

# Test different size ratios (1.0 to 4.0)
size_ratios = np.linspace(1.0, 4.0, 8)  # From equal size to 4x size
max_heights = []

# Print data table header
print("\nSize Ratio vs Max Height Data Points:")
print("Size Ratio\tMax Height (m)")
print("--------------------------------")

for ratio in size_ratios:
    mh = run_size_ratio_simulation(ratio)
    max_heights.append(mh)
    # Print data points in table format
    print(f"{ratio:.2f}\t\t{mh:.3f}")

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(size_ratios, max_heights, 'o-', color='darkblue', linewidth=2, markersize=8)
plt.xlabel('Size Ratio (Large/Small Particle Radius)', fontsize=12)
plt.ylabel('Maximum Height Reached (m)', fontsize=12)
plt.title('Brazil Nut Effect: Size Ratio vs. Segregation Height', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

# Add data point labels to the plot
for r, h in zip(size_ratios, max_heights):
    plt.text(r, h, f'({r:.1f}, {h:.2f})', 
             ha='center', va='bottom', fontsize=9, color='darkblue')

plt.tight_layout()
plt.savefig('size_ratio_vs_height.png', dpi=300, bbox_inches='tight')
plt.show()