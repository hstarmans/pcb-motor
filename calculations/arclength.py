# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Archimedean spiral
#
# ## Abstract
# A plot of an archimdean spiral and the calculation of its length.
# The length can also be obtained from KiCAD.  
#
#
# ## Parameters
# Each turn adds track_distance + track_width  
# b = (track_distance + track_width ) / 2*pi  
#   = (0.15 + 0.4)/(2*3.14) = 0.088  
# Start radius is 0.5 mm  
# a = 0.5  
# Startangle is 0 degrees, final angle is 12 turns, ergo $12*2*pi$.  

# +
import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(0., 10*2*np.pi, 1000)
a, b = 0.5, 0.088
plt.polar(theta, a+b*theta)
plt.show()


# -

def length_spiral(b, theta):
    return (b/2)*(theta*np.sqrt(1+theta**2)+np.log(theta+np.sqrt(1+theta**2)))


length_spiral(b, 10*2*np.pi)

# ## Conclusion
# In KiCAD, I find a length of 163. I assume, the apporoximation by line piecess lowers the track length.


