import numpy as np
a = np.array([[1, 2], [3, 4]])
z = np.zeros((3, 3), dtype=a.dtype)
print(np.c_[a, z])