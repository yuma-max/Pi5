"""
不規則配置データから等高線（Contour Map）を描画するツール

平面上の n 個の点 (x, y) と対応する値 z を基に、
Delaunay 三角分割 → グリッド補間 → 等高線追跡 の流れで滑らかな等高線を生成する。
"""

import numpy as np
from scipy.interpolate import LinearNDInterpolator, CloughTocher2DInterpolator
from scipy.spatial import Delaunay
import matplotlib
matplotlib.use("Agg")  # ヘッドレス環境でも画像保存可能（対話表示は別途 TkAgg 等を指定可）
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
    観測点の範囲をカバーする等間隔格子 (X_grid, Y_grid) を生成する。

    Parameters
    ----------
    x, y : array-like
        観測点の x, y 座標
    n_grid : int
        各軸のグリッド数（格子は n_grid × n_grid）
    margin_ratio : float
        範囲外へのマージン（0～1、範囲の割合）

    Returns
    -------
    X_grid, Y_grid : ndarray
        2次元格子座標
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
    Delaunay 三角分割に基づき、格子点上で z を補間する。

    Parameters
    ----------
    x, y, z : array-like
        観測点の座標と値
    X_grid, Y_grid : ndarray
        格子座標（build_grid の戻り値）
    method : 'linear' | 'cubic'
        'linear': 線形補間（三角形内で線形）
        'cubic': Clough-Tocher スプライン（C1 連続）

    Returns
    -------
    Z_grid : ndarray
        格子点上の補間値。三角形外は np.nan。
    """
    points = np.column_stack([np.asarray(x, dtype=float), np.asarray(y, dtype=float)])
    z = np.asarray(z, dtype=float).ravel()

    if method == "linear":
        interp = LinearNDInterpolator(points, z, fill_value=np.nan)
    elif method == "cubic":
        interp = CloughTocher2DInterpolator(points, z, fill_value=np.nan)
    else:
        raise ValueError("method は 'linear' または 'cubic' を指定してください")

    # 格子点をまとめて評価
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
    不規則な (x, y, z) から等高線図を描画する。

    Parameters
    ----------
    x, y, z : array-like
        観測点の座標と値
    method : 'linear' | 'cubic'
        補間方法
    n_grid : int
        補間用グリッドの解像度
    levels : int or array-like
        等高線の本数（int）またはレベル値のリスト
    show_scatter : bool
        観測点をプロットするか
    show_labels : bool
        等高線にラベルを付けるか
    cmap : str
        カラーマップ名（matplotlib）
    figsize, title, ax
        図のサイズ・タイトル・既存 Axes（ax を渡すとその Axes に描画）

    Returns
    -------
    fig, ax : Figure, Axes
    """
    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()
    z = np.asarray(z).ravel()
    if not (len(x) == len(y) == len(z)):
        raise ValueError("x, y, z の長さを揃えてください")

    X_grid, Y_grid = build_grid(x, y, n_grid=n_grid, margin_ratio=0.1)
    Z_grid = interpolate_to_grid(x, y, z, X_grid, Y_grid, method=method)

    # 有効領域（少なくとも1点が含まれる三角形内）のみを使うため、
    # 外挿で nan になった部分をマスクして contour に渡すと安全
    Z_plot = np.ma.masked_invalid(Z_grid)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # 塗りつぶし等高線（背景のグラデーション）
    cs = ax.contourf(X_grid, Y_grid, Z_plot, levels=levels, cmap=cmap, extend="both")
    # 等高線（線）
    cs_lines = ax.contour(X_grid, Y_grid, Z_plot, levels=levels, colors="k", linewidths=0.5, alpha=0.6)
    if show_labels:
        ax.clabel(cs_lines, inline=True, fontsize=8)

    if show_scatter:
        ax.scatter(x, y, c="black", s=20, alpha=0.8, zorder=5, label="観測点")

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
    与えられた点の Delaunay 三角分割を返す（デバッグ・可視化用）。

    Parameters
    ----------
    x, y : array-like
        点の座標

    Returns
    -------
    tri : scipy.spatial.Delaunay
    """
    points = np.column_stack([np.asarray(x).ravel(), np.asarray(y).ravel()])
    return Delaunay(points)


if __name__ == "__main__":
    # 使用例: ランダムな観測点から等高線を描画
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
        title="不規則データからの等高線（Cubic 補間）",
    )
    plt.tight_layout()
    plt.savefig("contour_example.png", dpi=150, bbox_inches="tight")
    print("contour_example.png を出力しました")
