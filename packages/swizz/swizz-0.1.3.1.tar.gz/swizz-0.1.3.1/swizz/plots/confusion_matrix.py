from swizz.plots._registry import register_plot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors

@register_plot(
    name="confusion_matrix",
    description="Plot a confusion matrix heatmap with optional normalization and annotations.",
    args=[
        {"name": "cm", "type": "pd.DataFrame", "required": True,
         "description": "Confusion matrix as a pandas DataFrame (shape N×N)."},
        {"name": "labels", "type": "List[str]", "required": False,
         "description": "List of class labels, length N, corresponding to matrix indices. If None, use DataFrame index/columns."},
        {"name": "figsize", "type": "tuple", "required": False,
         "description": "Figure size, e.g., (8, 6)."},
        {"name": "cmap", "type": "str", "required": False,
         "description": "Matplotlib colormap name, e.g., 'Blues'."},
        {"name": "normalize", "type": "bool", "required": False,
         "description": "If True, normalize rows to sum to 1 before plotting."},
        {"name": "title", "type": "str", "required": False,
         "description": "Optional title for the plot."},
        {"name": "fmt", "type": "str", "required": False,
         "description": "Format string for annotations, e.g., 'd' or '.2f'."},
        {"name": "cbar", "type": "bool", "required": False,
         "description": "Whether to display the colorbar."},
        {"name": "save", "type": "str", "required": False,
         "description": "Base filename to save PNG and PDF outputs."},
    ],
    example_code="confusion_matrix.py",
    example_image="confusion_matrix.png",
)
def plot(
    cm,
    labels=None,
    figsize=(8, 6),
    cmap='Blues',
    normalize=False,
    title=None,
    fmt='d',
    cbar=True,
    save=None,
    ax=None,
):
    # Create figure and axis if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # Automatically use labels from DataFrame if not provided
    if labels is None:
        labels = cm.index.tolist()

    # Get matrix values for operations
    cm_values = cm.values

    # Normalize rows if needed
    if normalize:
        row_sums = cm_values.sum(axis=1, keepdims=True)
        cm_values = np.divide(cm_values, row_sums, where=row_sums != 0)

    # Plot the matrix
    im = ax.imshow(cm_values, interpolation='nearest', cmap=cmap)
    if cbar:
        fig.colorbar(im, ax=ax)

    # Annotation threshold for text color
    thresh = cm_values.max() / 2.
    n_rows, n_cols = cm_values.shape
    for i in range(n_rows):
        for j in range(n_cols):
            val = cm_values[i, j]
            color = 'white' if val > thresh else 'black'
            ax.text(j, i, format(val, fmt),
                    ha='center', va='center',
                    color=color, fontweight='bold')

    # Axis labels and ticks
    ax.set_xlabel('Predicted label')
    ax.set_ylabel('True label')
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    # Title and layout
    ax.set_title(title)
    plt.tight_layout()

    # Save if requested
    if save:
        plt.savefig(f"{save}.png", dpi=300, bbox_inches='tight')
        plt.savefig(f"{save}.pdf", dpi=300, bbox_inches='tight')

    return fig, ax
