import matplotlib.pyplot as plt
import numpy as np
import random
a = {}
for i in range(10):
    a[i] = random.randint(1, 100)
print(a)

print(type(a.items()))
