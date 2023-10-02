import matplotlib.pyplot as plt
import numpy as np


def heatmap2d(arr, i):
    plot = plt.figure(i)
    plt.imshow(arr, cmap='viridis')
    plt.colorbar()

def hist(arr, i):
    plot = plt.figure(i)
    arr = arr.flatten()
    plt.hist(arr, density=True, bins=arr.max())  # density=False would make counts
    plt.ylabel('Probability')
    plt.xlabel('Dist')