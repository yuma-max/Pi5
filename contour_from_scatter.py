"""
Tool for drawing contour maps from irregularly placed data.

Generates smooth contours from n points (x, y) with corresponding z values via:
Delaunay triangulation -> grid interpolation -> contour tracing.
"""

import numpy as np
from scipy.interpolate import LinearNDInterpolator, CloughTocher2DInterpolator
from scipy.spatial import Delaunay
import matplotlib
matplotlib.use("Agg")  # Enables image saving in headless environments (use TkAgg etc. for interactive display)
import matplotlib.pyplot as plt
from matplotlib import cm
from typing import Literal, Optional, Tuple, List, Union


def build_grid(
    x: np.ndarray,
    y: np.ndarray,
    n_grid: int = 100,
    margin_ratio: float = 0.1,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build an evenly spaced grid (X_grid, Y_grid) covering the observation points.

    Parameters
    ----------
    x, y : array-like
        x, y coordinates of observation points
    n_grid : int
        Number of grid points per axis (grid is n_grid x n_grid)
    margin_ratio : float
        Margin outside the range (0-1, fraction of range)

    Returns
    -------
    X_grid, Y_grid : ndarray
        2D grid coordinates
    """
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    dx = (x_max - x_min) or 1.0
    dy = (y_max - y_min) or 1.0
    margin_x = dx * margin_ratio
    margin_y = dy * margin_ratio
    xi = np.linspace(x_min - margin_x, x_max + margin_x, n_grid)
    yi = np.linspace(y_min - margin_y, y_max + margin_y, n_grid)
    X_grid, Y_grid = np.meshgrid(xi, yi)
    return X_grid, Y_grid


def interpolate_to_grid(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    X_grid: np.ndarray,
    Y_grid: np.ndarray,
    method: Literal["linear", "cubic"] = "linear",
) -> np.ndarray:
    """
    Interpolate z on grid points based on Delaunay triangulation.

    Parameters
    ----------
    x, y, z : array-like
        Coordinates and values of observation points
    X_grid, Y_grid : ndarray
        Grid coordinates (return value of build_grid)
    method : 'linear' | 'cubic'
        'linear': Linear interpolation (linear within each triangle)
        'cubic': Clough-Tocher spline (C1 continuous)

    Returns
    -------
    Z_grid : ndarray
        Interpolated values on the grid. np.nan outside triangles.
    """
    points = np.column_stack([np.asarray(x, dtype=float), np.asarray(y, dtype=float)])
    z = np.asarray(z, dtype=float).ravel()

    if method == "linear":
        interp = LinearNDInterpolator(points, z, fill_value=np.nan)
    elif method == "cubic":
        interp = CloughTocher2DInterpolator(points, z, fill_value=np.nan)
    else:
        raise ValueError("method must be 'linear' or 'cubic'")

    # Evaluate interpolator at all grid points
    grid_points = np.column_stack([X_grid.ravel(), Y_grid.ravel()])
    Z_flat = interp(grid_points)
    Z_grid = Z_flat.reshape(X_grid.shape)
    return Z_grid


def plot_contour(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    *,
    method: Literal["linear", "cubic"] = "linear",
    n_grid: int = 100,
    levels: Optional[Union[int, List[float], np.ndarray]] = 15,
    show_scatter: bool = True,
    show_labels: bool = True,
    cmap: str = "viridis",
    figsize: Tuple[float, float] = (8, 6),
    title: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Draw a contour plot from irregular (x, y, z) data.

    Parameters
    ----------
    x, y, z : array-like
        Coordinates and values of observation points
    method : 'linear' | 'cubic'
        Interpolation method
    n_grid : int
        Resolution of the interpolation grid
    levels : int or array-like
        Number of contour levels (int) or list of level values
    show_scatter : bool
        Whether to plot observation points
    show_labels : bool
        Whether to add labels to contour lines
    cmap : str
        Colormap name (matplotlib)
    figsize, title, ax
        Figure size, title, and existing Axes (if ax is given, draw on that Axes)

    Returns
    -------
    fig, ax : Figure, Axes
    """
    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()
    z = np.asarray(z).ravel()
    if not (len(x) == len(y) == len(z)):
        raise ValueError("x, y, z must have the same length")

    X_grid, Y_grid = build_grid(x, y, n_grid=n_grid, margin_ratio=0.1)
    Z_grid = interpolate_to_grid(x, y, z, X_grid, Y_grid, method=method)

    # Mask extrapolated NaN regions for safe contour plotting
    Z_plot = np.ma.masked_invalid(Z_grid)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # Filled contours (background gradient)
    cs = ax.contourf(X_grid, Y_grid, Z_plot, levels=levels, cmap=cmap, extend="both")
    # Contour lines
    cs_lines = ax.contour(X_grid, Y_grid, Z_plot, levels=levels, colors="k", linewidths=0.5, alpha=0.6)
    if show_labels:
        ax.clabel(cs_lines, inline=True, fontsize=8)

    if show_scatter:
        ax.scatter(x, y, c="black", s=20, alpha=0.8, zorder=5, label="Observation points")

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal")
    if title:
        ax.set_title(title)
    plt.colorbar(cs, ax=ax, label="z")
    ax.legend(loc="upper right")

    return fig, ax


def get_delaunay_triangulation(x: np.ndarray, y: np.ndarray) -> Delaunay:
    """
    Return Delaunay triangulation of the given points (for debugging/visualization).

    Parameters
    ----------
    x, y : array-like
        Point coordinates

    Returns
    -------
    tri : scipy.spatial.Delaunay
    """
    points = np.column_stack([np.asarray(x).ravel(), np.asarray(y).ravel()])
    return Delaunay(points)


if __name__ == "__main__":
    # Example: draw contours from random observation points
    np.random.seed(42)
    n = 80
    x = np.random.rand(n) * 10
    y = np.random.rand(n) * 8
    z = np.sin(x * 0.5) * np.cos(y * 0.4) + 0.1 * (x - 5) ** 2

    fig, ax = plot_contour(
        x, y, z,
        method="cubic",
        n_grid=150,
        levels=20,
        show_scatter=True,
        show_labels=True,
        cmap="viridis",
        title="Contour from irregular data (Cubic interpolation)",
    )
    plt.tight_layout()
    plt.savefig("contour_example.png", dpi=150, bbox_inches="tight")
    print("Saved contour_example.png")
