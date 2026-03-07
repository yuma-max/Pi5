# 不規則データ用 等高線描画ツール（Contour Map）

平面上に不規則に配置された $n$ 個の点 $(x, y)$ と、それに対応する値 $z$ を基に、xy 平面上に滑らかな**等高線（Contour Map）**を描画するためのツールです。

## 概要

通常、等高線を描画するには整列された格子状のデータ（メッシュデータ）が必要ですが、本プログラムは**線形補間（Linear Interpolation）**および**スプライン補間（Cubic）**を用いることで、ランダムに配置された観測データからでも等高線を生成します。

## 主な機能

- **不規則データの処理**: 任意の座標 $(x_i, y_i, z_i)$ から等高線を自動生成
- **補間アルゴリズム**: **Linear**（線形）または **Cubic**（Clough-Tocher スプライン）を選択可能
- **カラーマップ対応**: データの値に応じたグラデーション表示
- **カスタマイズ性**: 等高線の間隔（レベル）やラベル表示を自由に設定

## 仕組みとアルゴリズム

1. **Delaunay 三角分割**: 与えられた $n$ 個の点を結び、重なりのない三角形の網を構築します。
2. **グリッド補間**: 三角形内を補間し、等間隔の格子状データ $Z_{grid} = f(X_{grid}, Y_{grid})$ を算出します。
3. **等高線追跡**: 算出された格子に対し、matplotlib の内部でマーチングスクエア法（Marching Squares）等を用いて等高線を抽出・描画します。

## セットアップ

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な描画

```python
from contour_from_scatter import plot_contour
import numpy as np

# 観測点 (x, y, z)
x = np.array([...])
y = np.array([...])
z = np.array([...])

fig, ax = plot_contour(x, y, z, method="cubic", levels=20)
fig.savefig("contour.png")
```

### 補間のみ使う場合

```python
from contour_from_scatter import build_grid, interpolate_to_grid

X_grid, Y_grid = build_grid(x, y, n_grid=100)
Z_grid = interpolate_to_grid(x, y, z, X_grid, Y_grid, method="linear")
# Z_grid を任意の方法で可視化・解析可能
```

### コマンドラインからサンプル実行

```bash
python contour_from_scatter.py
```

サンプルデータで等高線を描画し、`contour_example.png` を出力します。  
（ディスプレイのない環境では `MPLBACKEND=Agg` が自動で使われます。Segfault が出る場合は `pip install --upgrade scipy matplotlib` を試してください。）

## ファイル構成

- `contour_from_scatter.py` … メインの等高線描画モジュール
- `requirements.txt` … 依存パッケージ（numpy, scipy, matplotlib）
- `README.md` … 本ドキュメント

## ライセンス

Pi5 Project の一部です。
