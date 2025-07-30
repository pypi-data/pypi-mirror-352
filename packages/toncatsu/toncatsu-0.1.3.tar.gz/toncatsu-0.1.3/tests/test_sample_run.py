# -*- coding: utf-8 -*-
"""
Created on Wed May 28 15:57:44 2025

@author: hhasada
"""

# -*- coding: utf-8 -*-

import os

import pandas as pd
from toncatsu import toncatsu

dataset_dir = "sample_data"
output_dir = "sample_output"

# prepare input data
node_df = pd.read_csv(os.path.join(dataset_dir, "00000000.nodes"),sep="\t", header=None, dtype=str, encoding="utf-8")
node_df.columns = ['x_coord', 'y_coord'] + [f'col{i}' for i in range(node_df.shape[1] - 2)]
node_df = node_df[['x_coord', 'y_coord']].copy()
node_df['node_id'] = node_df.index
node_df['node_id'] = node_df['node_id'].astype(int)
node_df['x_coord'] = node_df['x_coord'].astype(float)
node_df['y_coord'] = node_df['y_coord'].astype(float)

link_df = pd.read_csv(os.path.join(dataset_dir, "00000000.arcs"),sep="\t", header=None, dtype=str, encoding="utf-8")
link_df.columns = ['from_node_id', 'to_node_id'] + [f'col{i}' for i in range(link_df.shape[1] - 2)]
link_df = link_df[['from_node_id', 'to_node_id']].copy()
link_df['link_id'] = link_df.index
link_df['from_node_id'] = link_df['from_node_id'].astype(int)
link_df['to_node_id'] = link_df['to_node_id'].astype(int)
link_df['link_id'] = link_df.index.astype(int)
link_df = pd.DataFrame(link_df)

obs_df = pd.read_csv(os.path.join(dataset_dir, "00000000.track"),sep="\t", header=None, dtype=str, encoding="utf-8")
obs_df.columns = ['x_coord', 'y_coord'] + [f'col{i}' for i in range(obs_df.shape[1] - 2)]
obs_df = obs_df[['x_coord', 'y_coord']].copy()
obs_df.columns = ['x_coord', 'y_coord']
obs_df['id'] = obs_df.index
obs_df['id'] = obs_df['id'].astype(int)
obs_df['x_coord'] = obs_df['x_coord'].astype(float)
obs_df['y_coord'] = obs_df['y_coord'].astype(float)

# map-matching
os.makedirs(output_dir, exist_ok=True)
data = toncatsu(link_df, node_df, obs_df, output_dir, split_length=10)

# verify
data.set_truth(os.path.join(dataset_dir, '00000000.route'))
arr, iarr = data.verify_matching()
print("ARR: ", arr, ", IARR: ", iarr)