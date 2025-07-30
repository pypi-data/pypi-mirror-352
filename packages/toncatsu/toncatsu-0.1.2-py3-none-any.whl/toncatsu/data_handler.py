# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import networkx as nx
import math
import geopandas as gpd
import os
from shapely.geometry import Point, LineString

def read_df(datapath, header):

    if datapath.endswith("csv"):
        df = pd.read_csv(datapath, header=header)
    elif datapath.endswith("geojson"):
        df = gpd.read_file(datapath)
    else:
        df = pd.read_csv(datapath, sep='\t', header=header)

    return df

def get_utm_epsg(latitude: float, longitude: float) -> int:
    """
    緯度経度から対応するUTMゾーンのEPSGコードを取得する関数（WGS84基準）
    
    Parameters:
        latitude (float): 緯度（-90〜90）
        longitude (float): 経度（-180〜180）

    Returns:
        int: EPSGコード（例：32654 for UTM zone 54N）
    """
    if not -80.0 <= latitude <= 84.0:
        raise ValueError("UTM座標系は緯度84N〜80Sまでが対象です。")
    
    # UTMゾーンの計算
    zone = int((longitude + 180) / 6) + 1
    
    # 北半球ならEPSG: 326XX, 南半球ならEPSG: 327XX
    if latitude >= 0:
        epsg_code = 32600 + zone
    else:
        epsg_code = 32700 + zone

    return  "EPSG:"+str(epsg_code)


class _Trajectory:
    def __init__(self): 

        self.trajectory = self._TrajectoryData()
 

    class _TrajectoryData:
        pass

    def set_observation(self, datapath, id_col=0, x_col=1, y_col=2, header=None):
 

        df = read_df(datapath, header)
        if id_col == None:
            df["id"] = df.index
        columns=list(df.columns)
        columns[id_col]="id"
        columns[x_col]="x"
        columns[y_col]="y"
        df.columns=columns
        self.trajectory.observation_df = df  # [["id","x","y"]]

    def read_observation(self, observation_df: pd.DataFrame):
        """
        Read GPS observation data from a DataFrame.

        Parameters
        ----------
        observation_df : pd.DataFrame
            A DataFrame with the following required columns:
            - 'id': Observation point ID.
            - 'x_coord': Longitude or projected X coordinate.
            - 'y_coord': Latitude or projected Y coordinate.

        Notes
        -----
        The function converts the coordinate columns into a GeoDataFrame 
        with WGS84 CRS (EPSG:4326).
        """
        gdf = gpd.GeoDataFrame(
            observation_df.copy(),
            geometry=gpd.points_from_xy(observation_df['x_coord'], observation_df['y_coord']),
            crs="EPSG:4326"
        )
        self.trajectory.observation_df = gdf.rename(columns={
            'x_coord': 'x',
            'y_coord': 'y'
        })
    

    def set_truth(self, datapath, header=None):
 

        df = read_df(datapath, header)
        self.trajectory.truth_array = np.ravel(df.values)
 

class _Network:
    def __init__(self):
 

        self.network = self._NetworkData()
 

    class _NetworkData:
        pass

    def set_node(self, datapath, id_col=0, x_col=1, y_col=2, header=None):
 

        df = read_df(datapath, header)
        if id_col == None:
            df["id"] = df.index
        columns=list(df.columns)
        columns[id_col]="id"
        columns[x_col]="x"
        columns[y_col]="y"
        df.columns=columns
        self.network.node_df = df  # [["id","x","y"]]
 

    def set_link(self, datapath, id_col=0, source_col=1, target_col=2, header=None):
 

        df = read_df(datapath, header)
        if id_col == None:
            df["id"] = df.index
        columns=list(df.columns)
        columns[id_col]="id"
        columns[source_col]="source"
        columns[target_col]="target"
        df.columns=columns
        self.network.link_df = df  # [["id", 'source','target']]
 
    def read_node(self, node_df: pd.DataFrame):
        """
        Read node data from a DataFrame (GMNS format).

        Parameters
        ----------
        node_df : pd.DataFrame
            A DataFrame with the following required columns:
            - 'node_id': Unique identifier for each node.
            - 'x_coord': X coordinate (longitude or projected X).
            - 'y_coord': Y coordinate (latitude or projected Y).

        Notes
        -----
        The function renames these columns to internal standard names:
        - 'id' for node_id
        - 'x'  for x_coord
        - 'y'  for y_coord
        """
        self.network.node_df = node_df.rename(columns={
            'node_id': 'id',
            'x_coord': 'x',
            'y_coord': 'y'
        })

    def read_link(self, link_df: pd.DataFrame):
        """
        Read link data from a DataFrame (GMNS format).

        Parameters
        ----------
        link_df : pd.DataFrame
            A DataFrame with the following required columns:
            - 'link_id': Unique identifier for each link.
            - 'from_node_id': Source node ID.
            - 'to_node_id': Target node ID.
            - 'geometry': LineString geometry.

        Notes
        -----
        The function renames these columns to:
        - 'id', "source", "target" respectively.
        """
        self.network.link_df = link_df.rename(columns={
            'link_id': 'id',
            'from_node_id': "source",
            'to_node_id': "target"
        })


    def _calc_linklength(self, n1_x, n1_y, n2_x, n2_y):
 
 
        return math.sqrt((n1_x - n2_x) ** 2 + (n1_y - n2_y) ** 2)

    def _set_linkweight(self, G):
 

        for e in G.edges:
            n1, n2 = G.nodes[e[0]], G.nodes[e[-1]]
            G.edges[e]["weight"] = self._calc_linklength(n1["x"], n1["y"], n2["x"], n2["y"])
 
        return G

    def _setup_graph(self, G):
 

        self.network.link_id_dict = nx.get_edge_attributes(G, "id")
        self.network.link_id_dict_inv = {v: k for k, v in self.network.link_id_dict.items()}

        node_dict = self.network.node_df.to_dict(orient='index')
        nx.set_node_attributes(G, node_dict)

        self.network.node_id_dict = nx.get_node_attributes(G, "id")
        self.network.node_id_dict_inv = {v: k for k, v in self.network.node_id_dict.items()}

        G = self._set_linkweight(G)
        self.network.G = G
 

    def get_node_df_of_G(self):
 

        df = self.network.node_df[
            self.network.node_df["id"].isin(list(nx.get_node_attributes(self.network.G, "id").values()))]
 
        return df

    def get_node_df_of_argG(self, G):
        df = self.network.node_df[
            self.network.node_df["id"].isin(list(nx.get_node_attributes(G, "id").values()))]
        return df

    def get_link_df_of_G(self):
 

        df = self.network.link_df[
            self.network.link_df["id"].isin(list(nx.get_edge_attributes(self.network.G, "id").values()))]
 
        return df

    def get_link_df_of_argG(self, G):
        df = self.network.link_df[
            self.network.link_df["id"].isin(list(nx.get_edge_attributes(G, "id").values()))]
        return df

    def transform_nodes_to_links(self, nodes):
 

        edge_id_list = []
        if len(nodes) >= 1:
            for i in range(len(nodes) - 1):
                s = self.get_node_index_of_G(nodes[i])
                t = self.get_node_index_of_G(nodes[i + 1])
                if self.network.G.has_edge(s, t):
                    edge_id = self.network.G.edges[s, t]["id"]
                    edge_id_list.append(edge_id)
 
        return edge_id_list

    def get_link_index_of_G(self, link_id):
 

        if type(link_id) == list:
            link_index = [self.network.link_id_dict_inv[_link_id] for _link_id in link_id]
        else:
            link_index = self.network.link_id_dict_inv[link_id]
 
        return link_index

    def get_node_index_of_G(self, node_id):
 

        if type(node_id) == list:
            node_index = [self.network.node_id_dict_inv[_node_id] for _node_id in node_id]
        else:
            node_index = self.network.node_id_dict_inv[node_id]
 
        return node_index
    
    def get_length_by_id(self,link_id):
        G = self.network.G_total
        for u, v, data in G.edges(data = True):
            if data.get("id") == link_id:
                return data.get("weight", None)
            elif str(data.get("id")) == str(link_id):
                return data.get("weight", None)
        return None  # 見つからない場合

    def make_link_geom(self):
 

        if not hasattr(self.network, 'link_gdf'):
            _gdf=self.network.link_df.copy()
            _gdf["geometry"]=None
            self.network.link_gdf=gpd.GeoDataFrame(_gdf)
            for i in self.network.link_gdf.index:
                s, t = self.network.link_gdf["source"][i], self.network.link_gdf["target"][i]
                s_x, s_y, *_ = self.network.node_df.loc[self.network.node_df["id"]==s,["x","y"]].values.tolist()[0]
                t_x, t_y, *_ = self.network.node_df.loc[self.network.node_df["id"] == t, ["x", "y"]].values.tolist()[0]
                self.network.link_gdf.loc[i,"geometry"] = LineString([(s_x, s_y), (t_x, t_y)])
            self.network.link_gdf["length"]=self.network.link_gdf["geometry"].apply(lambda x:x.length)
 

class Data(_Trajectory, _Network):
    def __init__(self):
        
 
        _Trajectory.__init__(self)
        _Network.__init__(self)


    def reproject_crs(self, to_crs= "EPSG:xxxx", from_crs="EPSG:4326"):
        
        if to_crs == "EPSG:xxxx":
            to_crs  = get_utm_epsg(self.trajectory.observation_df["x"].median(),self.trajectory.observation_df["y"].median())       
 
        self.trajectory.observation_df = self._func_reproject_crs(self.trajectory.observation_df, to_crs, from_crs)
        self.network.node_df = self._func_reproject_crs(self.network.node_df, to_crs, from_crs)
 

    def _func_reproject_crs(self, df, to_crs, from_crs):
 

        df = df.rename(columns={"x": f"x_{from_crs}", "y": f"y_{from_crs}"})
        df["geometry"] = df.apply(lambda x: Point(x[f"x_{from_crs}"], x[f"y_{from_crs}"]), axis=1)
        gdf = gpd.GeoDataFrame(df, crs=from_crs).to_crs(to_crs)
        df["x"] = gdf["geometry"].apply(lambda x: x.x)
        df["y"] = gdf["geometry"].apply(lambda x: x.y)
 
        return df

    def create_graph(self):
 

        G = nx.from_pandas_edgelist(self.network.link_df, "source", "target", "id", create_using=nx.DiGraph)
        self._setup_graph(G)
        self.network.G_total = self.network.G
        
        G = G.subgraph(max(nx.strongly_connected_components(G), key=len))  # delete unconnected subgraph
        self._setup_graph(G)
 

    def save_output(self,outout_dir,output_name=""):
        self.make_output()
        self.network.link_df_keiro.to_csv(os.path.join(outout_dir, f'{output_name}keiro.csv'),index=False,encoding="cp932")
        self.trajectory.observation_df_kyuchaku.to_csv(os.path.join(outout_dir, f'{output_name}kyuchaku.csv'),index=False,encoding="cp932")
    
    def make_output(self):
        self._make_kyuchaku()
        self._make_keiro()    
    
    def _make_kyuchaku(self):
       
        col1 = list(set(["id","source","target","id_original"])&set(self.network.link_df.columns))
        col2 = list(set(["source","target","id_original"])&set(self.network.link_df.columns))+["link_id"]
        
        # 吸着データを作成
        self.trajectory.observation_df_kyuchaku=self.trajectory.observation_df.copy()
        
        if self.config.nearest_neighborhood=="node":
        
            ## マップマッチングされたリンクの端点を全て抽出
            mapmatched_nodes = list(set(self.network.link_df[self.network.link_df["id"].isin(self.trajectory.mapmatched_array)][["source","target"]].values.flatten()))
            
            ## 最近傍ノードのうち、マップマッチングされたリンクの端点に含まれるものを抽出
            nearest_mapmatched_nodes_index=np.where(np.isin(self.trajectory.nearest_node_array,mapmatched_nodes))[0].tolist()
            
            ## マップマッチングされたリンクの端点に含まれる最近棒ノードをsourceとするlink_dfを抽出
            nearest_link_df = pd.DataFrame(self.trajectory.nearest_node_array,columns=["source"])\
                .merge(self.network.link_df[self.network.link_df["id"].isin(self.trajectory.mapmatched_array)],on="source",how="left").reset_index()[col1].replace([np.nan], [None])
            
            # マップマッチングされたリンクの端点に含まれる最近棒ノードとそれがsourceであるリンクの情報を紐づけ
            self.trajectory.observation_df_kyuchaku.loc[self.trajectory.observation_df_kyuchaku.index.isin(nearest_mapmatched_nodes_index),col2]\
                =nearest_link_df.loc[nearest_link_df.index.isin(nearest_mapmatched_nodes_index)].rename(columns={"id":"link_id"})
        
        elif self.config.nearest_neighborhood=="link":
            ## マップマッチングされたlink_dfを抽出
            nearest_link_df = pd.DataFrame(self.trajectory.nearest_array,columns=["id"])\
                .merge(self.network.link_df,on="id",how="left").reset_index()[col1].replace([np.nan], [None])
            
            # リンクの情報を紐づけ
            self.trajectory.observation_df_kyuchaku.loc[:,col2]\
                =nearest_link_df.loc[:].rename(columns={"id":"link_id"})
        
        
    def _make_keiro(self):
        # 経路データを作成
        self.network.link_df_keiro = pd.DataFrame({"id":self.trajectory.mapmatched_array})
        self.network.link_df_keiro = self.network.link_df_keiro.merge(self.network.link_df,on="id",how="left")
        
        j = 0
        #self.network.link_df_keiro["sokokanzensei"] = np.nan
        #self.network.link_df_keiro["ingoing_time"]= np.nan
        #self.network.link_df_keiro["outgoing_time"] = np.nan
        #self.network.link_df_keiro["traveltime"] = np.nan
        #self.network.link_df_keiro["velocity"] = np.nan
        #self.network.link_df_keiro["kansokutenkukanbango"] = np.nan
        #self.network.link_df_keiro["count_observation"] = np.nan
        self.network.link_df_keiro["ingoing_observation_id"] = np.nan
        self.network.link_df_keiro["outgoing_observation_id"] = np.nan
        
        ## 以下がボトルネックになっている
        for i in self.network.link_df_keiro.index:
            link_id = self.network.link_df_keiro["id"][i]
            if len(self.trajectory.observation_df_kyuchaku[(self.trajectory.observation_df_kyuchaku["link_id"]==link_id)&(self.trajectory.observation_df_kyuchaku.index>=j)])>0:
                ingoing = self.trajectory.observation_df_kyuchaku[(self.trajectory.observation_df_kyuchaku["link_id"]==link_id)&(self.trajectory.observation_df_kyuchaku.index>=j)].iloc[0,:]
                for jj in range(j,len(self.trajectory.observation_df_kyuchaku)):
                    if j < len(self.trajectory.observation_df_kyuchaku):
                        if jj < len(self.trajectory.observation_df_kyuchaku)-1:
                            if (self.trajectory.observation_df_kyuchaku["link_id"][jj] != None)&(self.trajectory.observation_df_kyuchaku["link_id"][jj] != self.trajectory.observation_df_kyuchaku["link_id"][jj+1]):
                                j = jj+ 1
                                break
                    else:
                        j == len(self.trajectory.observation_df_kyuchaku)
                outgoing= self.trajectory.observation_df_kyuchaku[(self.trajectory.observation_df_kyuchaku.index==j-1)].iloc[0,:]
                
                #self.network.link_df_keiro["ingoing_time"][i] = ingoing["time"]
                #self.network.link_df_keiro["outgoing_time"][i] = outgoing["time"]
                self.network.link_df_keiro.loc[i,"ingoing_observation_id"] = ingoing["id"]
                self.network.link_df_keiro.loc[i,"outgoing_observation_id"] = outgoing["id"]

    def verify_matching(self):

        # フルネット
        #test_G = self.data.network.G
        match_truth_array = set(self.trajectory.truth_array) & set(self.trajectory.mapmatched_array)
        match_not_truth_array = set(self.trajectory.mapmatched_array) - set(self.trajectory.truth_array)
        # print(match_truth_array)

        # ARR = length of correctly matched route / total length of correct route
        arr = 0.0
        tlcr = 0.0
        lcmr = 0.0

        for link in self.trajectory.truth_array:
            if self.get_length_by_id(link) != None:
                tlcr = tlcr + self.get_length_by_id(link)
            else:
                print('None 1:' + str(link))
        for link in match_truth_array:
            if self.get_length_by_id(link) != None:
                lcmr = lcmr + self.get_length_by_id(link)
            else:
                print('None 2:' + str(link))

        arr = lcmr / tlcr
        #print(str(arr) + ' = ' + str(lcmr) + ' / ' + str(tlcr))

        # IARR = length of incorrectly matched route / total length of matched route
        iarr = 0.0
        tlmr = 0.0
        limr = 0.0

        for link in self.trajectory.mapmatched_array:
            if self.get_length_by_id(link) != None:
                tlmr = tlmr + self.get_length_by_id(link)
            else:
                print('None 3:' + str(link))
        for link in match_not_truth_array:
            if self.get_length_by_id(link) != None:
                limr = limr + self.get_length_by_id(link)
            else:
                print('None 4:' + str(link))

        iarr = limr / tlmr
        #print(str(iarr) + ' = ' + str(limr) + ' / ' + str(tlmr))

        return arr, iarr
