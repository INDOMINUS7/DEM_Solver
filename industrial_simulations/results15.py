import numpy as np
import matplotlib.pyplot as plt
from ELEVENTH_TOY_PROBLEM import Particle, Box, Simulation

def calculate_rise_rate(size_ratio, amplitude=0.1, frequency=20.0, total_time=15.0):
    # Fixed parameters
    width, height = 1.0, 1.5
    spring_constant = 10000.0
    dt = 0.001
    small_r = 0.04
    density = 1000.0
    threshold = 0.8 * height  # 80% of container height
    
    # Calculate large particle size
    large_r = small_r * size_ratio
    
    # Initialize particles (60 small + 1 large)
    particles = []
    np.random.seed(42)
    for _ in range(60):
        x = np.random.uniform(small_r, width - small_r)
        y = np.random.uniform(0.2, 0.8)
        m = np.pi * small_r**2 * density
        particles.append(Particle(x, y, 0.0, 0.0, small_r, m))
    
    # Add large particle (start buried)
    large_mass = np.pi * large_r**2 * density
    particles.append(Particle(width/2, large_r + 0.05, 0.0, 0.0, large_r, large_mass))
    
    # Run simulation
    sim = Simulation(particles, Box(width, height, spring_constant), dt)
    rise_start_time = None
    rise_end_time = None
    
    for step in range(int(total_time/dt)):
        t = step * dt
        # Apply vibration with damping in upper region
        pseudo_acc = (2 * np.pi * frequency)**2 * amplitude * np.sin(2 * np.pi * frequency * t)
        for p in sim.particles:
            if p.y < height:  # Only apply to lower 70%
                p.vy += pseudo_acc * dt  # Reduced effectiveness
        
        pos = sim.runStep()
        current_height = pos[-1][1]  # y of large particle
        
        # Detect when particle starts rising (above initial position)
        if current_height > large_r + 0.15 and rise_start_time is None:
            rise_start_time = t
        
        # Detect when particle reaches threshold
        if current_height >= threshold and rise_end_time is None and rise_start_time is not None:
            rise_end_time = t
            break
    
    if rise_start_time and rise_end_time:
        rise_rate = (threshold - (large_r + 0.05)) / (rise_end_time - rise_start_time)
        return rise_rate
    else:
        return 0.0  # Return 0 if BNE didn't occur

# Test different size ratios (1.5 to 5.0)
size_ratios = np.linspace(1.5, 4.5, 10)  # More reasonable BNE range
rise_rates = []

print("Running size ratio rise rate tests...")
for ratio in size_ratios:
    rate = calculate_rise_rate(ratio)
    rise_rates.append(rate)
    print(f"Size ratio {ratio:.1f}: Rise rate = {rate:.4f} m/s")

# Plot results with enhanced styling
plt.figure(figsize=(12, 7))
plt.plot(size_ratios, rise_rates, 
         marker='o', 
         markersize=10,
         markerfacecolor='gold',
         markeredgecolor='darkred',
         markeredgewidth=2,
         color='darkred',
         linewidth=3,
         linestyle='-')

# Formatting
plt.xlabel('Size Ratio (Large/Small Particle Radius)', fontsize=14, fontweight='bold')
plt.ylabel('Rise Rate (m/s)', fontsize=14, fontweight='bold')
plt.title('Brazil Nut Effect: Particle Size Ratio vs. Rise Rate', 
          fontsize=16, pad=20, fontweight='bold')

# Annotations and grid
for i, (r, rate) in enumerate(zip(size_ratios, rise_rates)):
    plt.annotate(f'{rate:.3f} m/s', 
                 (r, rate), 
                 textcoords="offset points", 
                 xytext=(0,10), 
                 ha='center',
                 fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=1))

plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Highlight optimal range
optimal_min = 2.5
optimal_max = 3.5
plt.axvspan(optimal_min, optimal_max, color='green', alpha=0.1, label='Optimal BNE Range')
plt.legend(loc='upper right', fontsize=12)

plt.tight_layout()
plt.show()