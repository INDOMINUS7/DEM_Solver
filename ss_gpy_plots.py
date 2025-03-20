import matplotlib.pyplot as plt
import numpy as np

# Data from the simulation
configurations = [
    (1, 1, 32, 62.420294392),
    (1, 1, 64, 31.269314522),
    (1, 1, 128, 15.187319976),
    (1, 2, 32, 31.260056272),
    (1, 2, 64, 15.150166809),
    (1, 2, 128, 8.344742786),
    (1, 4, 32, 15.102151062),
    (1, 4, 64, 8.435840342),
    (1, 4, 128, 5.238115456),
    (2, 1, 32, 30.755772034),
    (2, 1, 64, 16.1211774),
    (2, 1, 128, 8.687224962),
    (2, 2, 32, 16.097770801),
    (2, 2, 64, 8.686667988),
    (2, 2, 128, 5.182447957),
    (2, 4, 32, 8.682683201),
    (2, 4, 64, 5.181760632),
    (2, 4, 128, 3.257637656),
    (4, 1, 32, 14.031352492),
    (4, 1, 64, 7.410494502),
    (4, 1, 128, 5.016393177),
    (4, 2, 32, 7.416186635),
    (4, 2, 64, 4.92861121),
    (4, 2, 128, 3.225354231),
    (4, 4, 32, 4.954187345),
    (4, 4, 64, 3.221384385),
    (4, 4, 128, 2.201187549),
    (8, 1, 32, 7.500736771),
    (8, 1, 64, 4.423049497),
    (8, 1, 128, 3.129160294),
    (8, 2, 32, 4.442541711),
    (8, 2, 64, 3.163461514),
    (8, 2, 128, 2.235269715),
    (8, 4, 32, 3.146146779),
    (8, 4, 64, 2.246230794),
    (8, 4, 128, 1.724500629),
]

# Extract data
gangs = [c[0] for c in configurations]
workers = [c[1] for c in configurations]
vector_lengths = [c[2] for c in configurations]
execution_times = [c[3] for c in configurations]

# Baseline execution time (1 gang, 1 worker, 32 vector length)
baseline_time = configurations[0][3]

# Calculate speedup
speedup = [baseline_time / t for t in execution_times]

# Create a dual y-axis plot for Execution Time and Speedup
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot Execution Time on the left y-axis
ax1.plot(range(len(configurations)), execution_times, marker='o', color='b', label='Execution Time (s)')
ax1.set_xlabel('Configuration Index')
ax1.set_ylabel('Execution Time (s)', color='b')
ax1.tick_params(axis='y', labelcolor='b')

# Create a second y-axis for Speedup
ax2 = ax1.twinx()
ax2.plot(range(len(configurations)), speedup, marker='o', color='r', label='Speedup')
ax2.set_ylabel('Speedup', color='r')
ax2.tick_params(axis='y', labelcolor='r')

# Add configuration labels to x-axis
config_labels = [f'G={g}, W={w}, VL={vl}' for g, w, vl, _ in configurations]
ax1.set_xticks(range(len(configurations)))
ax1.set_xticklabels(config_labels, rotation=90)

# Add title and legend
plt.title('Execution Time and Speedup for Different Configurations')
fig.tight_layout()
plt.legend(loc='upper left')
plt.grid()
plt.show()