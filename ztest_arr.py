import numpy as np

img_Arr = np.zeros((3, 3), dtype=np.uint8)
img_Arr[0, 0] = 1
img_Arr[0, 1] = 2
img_Arr[1, 0] = 3
img_Arr[1, 1] = 4
img_Arr[2, 2] = 5
print(img_Arr)
print("___________")
print(np.repeat(np.repeat(img_Arr, 2, axis=0), 2, axis=1))
