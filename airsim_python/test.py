import numpy as np
center = np.array([[0],[5]])
pos_reserve = np.array([[0.],[0.],[-3.]])
pos = [[6],[13],[10]]
dp = pos[0:2]-center
print(dp)
print(pos_reserve)
print("norm:",np.linalg.norm(dp))