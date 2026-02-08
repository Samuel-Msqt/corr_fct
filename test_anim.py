import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Data
x = np.linspace(0, 2 * np.pi, 500)

# Figure and axis
fig, ax = plt.subplots()
(line,) = ax.plot(x, np.sin(x))
ax.set_ylim(-1.2, 1.2)


# Initialization function
def init():
    line.set_ydata(np.zeros_like(x))
    return (line,)


# Update function (called for each frame)
def update(frame):
    line.set_ydata(np.sin(x + 0.1 * frame))
    return (line,)


# Create animation
ani = FuncAnimation(fig, update, frames=200, init_func=init, blit=True, interval=30)

# Save to video
ani.save("sine_wave.mp4", fps=30)

plt.close(fig)
