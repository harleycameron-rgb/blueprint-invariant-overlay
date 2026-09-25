import numpy as np
def tusi_position(theta,r=1.0):
 return (r*np.cos(theta)+r*np.cos(-theta), r*np.sin(theta)+r*np.sin(-theta))
