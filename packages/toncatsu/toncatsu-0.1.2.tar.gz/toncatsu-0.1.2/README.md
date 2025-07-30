# Toncatsu
[![PyPI version](https://badge.fury.io/py/toncatsu.svg)](https://pypi.org/project/toncatsu/)

A Python Library for Robust Observation-based Map-matching

頑健な観測ベースのマップマッチングを行うpythonライブラリ

## Overview 概要

**Toncatsu** is a Python library that is robust to GPS/GNSS errors and performs stable map-matching regardless of link segmentation. It is based on the map-matching method proposed by Hara (2017) for Catsudon, a mobile trajectory analysis tool, and maps observation points to the nearest link rather than the nearest node.

**Toncatsu**は、GPS/GNSS誤差への耐性を持ち、リンクの分割状況に左右されずに頑健なマップマッチングを行うPythonライブラリです。原（2017）が提案した移動軌跡解析ツールCatsudonのマップマッチング手法を発展させ、観測点を最も近いノードではなく最も近いリンクに対応づけます。

## Features 特徴

- 🌍 **Link-based matching**: Reduces sensitivity to sparse or dense node distributions  
  　　**リンク基準のマッチング**：ノードの疎密による経路のばらつきを低減
- 🚀 **Fast search via kd-tree**: Efficient nearest-link search using spatial trees  
  　　**kd-treeを活用した高速探索**：空間木構造により近傍リンクを迅速に取得
- 🐍 **Pure Python / GeoPandas-based**: Easy to install and integrate  
  　　**GeoPandasベースの純Python実装**：環境構築が容易で拡張性が高い
- 🧪 **Benchmark tested**: Evaluated using standardized test datasets  
  　**ベンチマーク検証済み**：標準データセットを用いた評価を実施

## Citation 引用
Coming soon!

## Acknowledgment 謝辞
This research was partially the result of the joint research with CSIS, the University of Tokyo (No. 1417) and used the following data: Real People Flow data provided by GeoTechnologies, Inc.

本研究は、東京大学CSIS共同研究（No. 1417）による成果を含む（利用データ: 実人流データ（ジオテクノロジーズ株式会社提供））。

## References 参考文献
- 原祐輔. 2017. “GPS軌跡解析器の開発と長期観測データを用いた新たな個人属性の提案.” In 第 55 回土木計画学研究発表会・講演集.
- 羽佐田紘之, 茂木渉, Yuhan Gao, and 岡英紀. 2024. “リンク分割を組み入れた頑健なマップマッチング手法の提案と比較.” In 第69回土木計画学研究発表会・講演集, C04-1.

---

## Installation インストール

```bash
pip install toncatsu
```


## Usage 使い方

```python
from toncatsu import toncatsu

# Required DataFrames: link_df, node_df, observation_df
toncatsu(link_df, node_df, observation_df, output_dir="./output", split_length=10)
```

## Function 関数

Function `toncatsu()` performs map-matching using [GMNS format](https://github.com/zephyr-data-specs/GMNS) node/link data and GPS observations.

関数`toncatsu()`は、[GMNSフォーマット](https://github.com/zephyr-data-specs/GMNS)のノード・リンクとGPS観測データを用いてマップマッチングを実行します。

**Parameters 引数:**

English
- `link_df`: DataFrame with columns: `'link_id'`, `'from_node_id'`, `'to_node_id'` (follows GMNS format)
- `node_df`: DataFrame with columns: `'node_id'`, `'x_coord'`, `'y_coord'` (follows GMNS format with EPSG:4326)
- `observation_df`: DataFrame with columns: `'id'`, `'x_coord'`, `'y_coord'`  
- `output_dir`: Output directory for saving results
- `split_length`: Segment length for link splitting in meters (default: 10)

日本語
- `link_df`: `'link_id'`, `'from_node_id'`, `'to_node_id'` を含むDataFrame (GMNSフォーマットに準拠) 
- `node_df`: `'node_id'`, `'x_coord'`, `'y_coord'` を含むDataFrame (GMNSフォーマットに準拠、EPSG:4326のみ対応) 
- `observation_df`: `'id'`, `'x_coord'`, `'y_coord'` を含むDataFrame  
- `output_dir`: 結果を保存する出力先ディレクトリ
- `split_length`: リンク分割の長さ(m) (デフォルト: 10)
