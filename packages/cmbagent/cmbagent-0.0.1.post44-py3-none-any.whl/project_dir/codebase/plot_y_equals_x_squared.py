# filename: codebase/plot_y_equals_x_squared.py
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Set matplotlib to not use LaTeX rendering
plt.rcParams['text.usetex'] = False

# Create data directory if it doesn't exist
database_path = "data"
if not os.path.exists(database_path):
    os.makedirs(database_path)

# Generate data for y = x^2
x = np.linspace(-10, 10, 500)  # x in arbitrary units
y = x ** 2  # y in arbitrary units

# Create the plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x, y, label="y = x^2", color="blue", linewidth=2)
ax.set_xlabel("x (arbitrary units)")
ax.set_ylabel("y (arbitrary units)")
ax.set_title("Plot of y = x^2")
ax.grid(True, which='both', linestyle='--', linewidth=0.5)
ax.legend()
plt.tight_layout()

# Generate timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plot_filename = "y_equals_x_squared_1_" + timestamp + ".png"
plot_filepath = os.path.join(database_path, plot_filename)

# Save the plot at high resolution
plt.savefig(plot_filepath, dpi=300)

# Print concise description
print("Plot of y = x^2 over the range x = -10 to 10 has been saved as:")
print(plot_filepath)
print("The plot shows a parabola with labeled axes, title, and grid lines.")