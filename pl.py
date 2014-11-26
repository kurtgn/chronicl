from matplotlib import pyplot as plt
from numpy import arange
x_points = arange(1,21)
baseline = arange(0,20)
plt.plot(x_points, baseline**2, "g-o", x_points, baseline, "r-^")
plt.show()