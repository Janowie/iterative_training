import pprint
from collections import defaultdict
import matplotlib.pyplot as plt


def plot_heatmap(data, labels):
  fig, ax = plt.subplots(1, len(data))
  for i, d in enumerate(data):
    ax[i].set_title(f"Label: {labels[i]}")
    ax[i].imshow(d.squeeze(), cmap='Blues')
