#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

log_arr = [
2, 3, 5, 9, 16, 27, 46, 80,139, 240, 416, 720, 1245, 2154, 3728, 6449, 11159, 19307, 33405, 57797]

fig, ax = plt.subplots(1,1)
ax.plot(log_arr, log_arr, 'o-')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('x')
ax.set_ylabel('y')
fig.tight_layout()
plt.show()
