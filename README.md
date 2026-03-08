# Contour Map Tool for Irregular Data

A tool for drawing smooth **contour maps** on the xy-plane from $n$ irregularly placed points $(x, y)$ with corresponding values $z$.

## Overview

Contour plots typically require regularly gridded (mesh) data. This program uses **linear interpolation** and **cubic spline interpolation** to generate contours from randomly placed observation data.

## Features

- **Irregular data handling**: Automatically generate contours from arbitrary coordinates $(x_i, y_i, z_i)$
- **Interpolation algorithms**: Choose **Linear** or **Cubic** (Clough-Tocher spline)
- **Colormap support**: Gradient display based on data values
- **Customization**: Freely set contour levels and label display

## Algorithm

1. **Delaunay triangulation**: Connect the given $n$ points to build a non-overlapping triangular mesh.
2. **Grid interpolation**: Interpolate within triangles to compute evenly spaced grid data $Z_{grid} = f(X_{grid}, Y_{grid})$.
3. **Contour tracing**: Extract and draw contours from the computed grid using the Marching Squares algorithm (via matplotlib).

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Basic plotting

```python
from contour_from_scatter import plot_contour
import numpy as np

# Observation points (x, y, z)
x = np.array([...])
y = np.array([...])
z = np.array([...])

fig, ax = plot_contour(x, y, z, method="cubic", levels=20)
fig.savefig("contour.png")
```

### Interpolation only

```python
from contour_from_scatter import build_grid, interpolate_to_grid

X_grid, Y_grid = build_grid(x, y, n_grid=100)
Z_grid = interpolate_to_grid(x, y, z, X_grid, Y_grid, method="linear")
# Z_grid can be visualized or analyzed as needed
```

### Run sample from command line

```bash
python contour_from_scatter.py
```

This draws contours from sample data and outputs `contour_example.png`.  
(`MPLBACKEND=Agg` is used automatically in headless environments. If you get a segfault, try `pip install --upgrade scipy matplotlib`.)

## File structure

- `contour_from_scatter.py` — Main contour plotting module
- `requirements.txt` — Dependencies (numpy, scipy, matplotlib)
- `README.md` — This document

## License

Part of the Pi5 Project.
