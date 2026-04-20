import matplotlib.pyplot as plt

# Data: (number of classes, runtime in seconds)
data = [
    (10, 0.09),
    (50, 0.09),
    (80, 0.08),
    (100, 0.07),
    (150, 0.07),
    (500, 0.07),
    (1000, 0.42),
    (10000, 20.48),
    # Add more points here if you collect more timings
]

x = [d[0] for d in data]
y = [d[1] for d in data]

plt.figure(figsize=(10,6))
plt.plot(x, y, marker='o', linestyle='-', color='b')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Number of Classes (log scale)')
plt.ylabel('Runtime (seconds, log scale)')
plt.title('Greedy Algorithm Time Analysis')
plt.grid(True, which="both", ls="--", lw=0.5)
plt.tight_layout()
plt.savefig('experiments/class_scale/greedy_time_analysis.jpeg', dpi=300)
plt.show()
