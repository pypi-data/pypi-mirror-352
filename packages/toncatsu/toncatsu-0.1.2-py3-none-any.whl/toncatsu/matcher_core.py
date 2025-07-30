import networkx as nx
import numpy as np
import pandas as pd
import scipy.spatial as ss
from time import time

class _Method_Base:
    def __init__(self):
        pass
    
    class _Config:
        pass
    
    def set_data(self,data):
        """
        dataクラスの入力
        
        Parameters
        ----------
        data : class
            The data class made in data.py.
        """
        
        self.data = data
        self.data.config=self._Config()
        
        self.data.config.start_time = time()

    def _calc_elapsedtime(self):
        """
        経過時間の計算
        """
        t2 = time() - self.data.config.start_time
        print('elapsed time of Toncatsu map-matching:', f"{t2}s")

class Toncatsu(_Method_Base):
    """
    Toncatsuを実行するクラス
    
    Attributes
    ----------
    self.data: class
        attributes are 
            self.data.trajectory.observation_df: pd.DataFrame
            self.data.network.node_df: pd.DataFrame
            self.data.network.link_df: pd.DataFrame
            
    
    """  

    def fit(self,nearest_neighborhood="link",interpolate_onlink=True,split_length=10):
        """
        Toncatsuを実行
        (1)最近傍ノード(リンク)探索：self._find_nearest_neighborhood(), self._find_nearest_neighborhood_link()
        (2)候補リンク抽出：self._interpolate_between_nodes(), self._interpolate_between_edges()
        (3)最短経路探索：self._find_shortestpath_on_subgraph()
        
        Parameters
        ----------
        interpolate_onlink : bool
            This effects when find the nearest edge on network. If True then interpolate points on edges. The interpolated points are found 
        """
        
        self.data.config.interpolate_onlink=interpolate_onlink
        self.data.config.nearest_neighborhood=nearest_neighborhood

        if self.data.config.nearest_neighborhood in ["node"]:
            #(1)最近傍ノード(リンク)探索
            nearest_nodes_id = self._find_nearest_neighborhood()
            
            #(2)候補リンク抽出
            interpolated_path = self._interpolate_between_nodes(nearest_nodes_id)
            self.data.trajectory.nearest_node_array = np.array(nearest_nodes_id)#データ格納
            
        elif self.data.config.nearest_neighborhood in ["edge","link"]:
            #(1)最近傍ノード(リンク)探索
            nearest_links_id,nearest_links_id_kyuchaku = self._find_nearest_neighborhood_link(split_length=split_length)
            self.data.trajectory.nearest_array = np.array(nearest_links_id_kyuchaku)#データ格納
            
            #(2)候補リンク抽出
            interpolated_path = self._interpolate_between_edges(nearest_links_id)
        self.data.trajectory.interpolated_array = np.array(interpolated_path)#データ格納
        
        #(3)最短経路探索
        mapmatched_path = self._find_shortestpath_on_subgraph(interpolated_path)
        self.data.trajectory.mapmatched_array = np.array(mapmatched_path)#データ格納
        
        #所要時間計算
        self._calc_elapsedtime()

    def _kdtree(self,point):
        sci_kdt = ss.KDTree(point, leafsize=30)
        t = time()
        res_kdtree = sci_kdt.query(self.data.trajectory.observation_df[["x", "y"]], k=1)
        t2 = time() - t
        #rint('elapsed time of kdtree:', f"{t2}s")
        return res_kdtree

    def _find_nearest_neighborhood_link(self,split_length):
        if self.data.config.interpolate_onlink:
            self.data.make_link_geom()
            nearest_links_id,nearest_links_id_kyuchaku = self._find_nearest_neighborhood_interpolated(dist=split_length)
        else:
            nearest_nodes_id = self._find_nearest_neighborhood()
            nearest_links_id = self.data.transform_nodes_to_links(nearest_nodes_id)
            nearest_links_id_kyuchaku = None
        #print("nearest links: " + str(nearest_links_id))

        return nearest_links_id,nearest_links_id_kyuchaku

    def _find_nearest_neighborhood(self):
        res_kdtree = self._kdtree(point=self.data.get_node_df_of_G()[["x", "y"]])

        node_id_array = self.data.get_node_df_of_G()["id"].values
        nearest_nodes_id = [node_id_array[i] for i in res_kdtree[1]]

        return nearest_nodes_id

    def _find_nearest_neighborhood_interpolated(self,dist=10):
        #self._calc_elapsedtime()
        link_id_list=[]
        point_list=[]
        for i in self.data.network.link_gdf[self.data.network.link_gdf.index.isin(list(self.data.get_link_df_of_G().index))].index:
            link_id = self.data.network.link_gdf["id"][i]
            num_vert = max(round(self.data.network.link_gdf["length"][i] / dist), 1)
            for n in range(num_vert + 1):
                point = self.data.network.link_gdf["geometry"][i].interpolate(n / num_vert, normalized=True)
                point_list.append([point.x, point.y])
                link_id_list.append(link_id)

        res_kdtree = self._kdtree(point=point_list)
        nearest_links_id_kyuchaku = [link_id_list[i] for i in res_kdtree[1]]
        nearest_links_id=[nearest_links_id_kyuchaku[0]]
        if len(nearest_links_id_kyuchaku)>=2:
            for i in range(len(nearest_links_id_kyuchaku)-1):
                if nearest_links_id_kyuchaku[i]!=nearest_links_id_kyuchaku[i+1]:
                    nearest_links_id.append(nearest_links_id_kyuchaku[i+1])
        #self._calc_elapsedtime()

        return nearest_links_id,nearest_links_id_kyuchaku

    def _interpolate_between_edges(self, nearest_links_id):
        interpolated_path = nearest_links_id.copy()
        for e1_i in range(len(nearest_links_id) - 1):
            e2_i = e1_i + 1
            e1_id, e2_id = nearest_links_id[e1_i], nearest_links_id[e2_i]
            e1_t = self.data.get_link_index_of_G(e1_id)[1]#[0][1]
            e2_s = self.data.get_link_index_of_G(e2_id)[0]#[0][0]
            if e1_t != e2_s:
                length, interpolation_nodebased = nx.single_source_dijkstra(self.data.network.G, e1_t, e2_s,
                                                                            weight="weight")
                insert_index = interpolated_path.index(nearest_links_id[e2_i])
                interpolated_path[insert_index: insert_index] = self.data.transform_nodes_to_links(
                    interpolation_nodebased)
        #print("interpolated path: " + str(interpolated_path))

        return interpolated_path

    def _interpolate_between_nodes(self, nearest_nodes_id):
        interpolated_path = []
        for n1_i in range(len(nearest_nodes_id) - 1):
            n2_i = n1_i + 1
            n1_id, n2_id = nearest_nodes_id[n1_i], nearest_nodes_id[n2_i]
            n1 = self.data.get_node_index_of_G(n1_id)
            n2 = self.data.get_node_index_of_G(n2_id)
            if n1 != n2:
                length, interpolation_nodebased = nx.single_source_dijkstra(self.data.network.G, n1, n2,
                                                                            weight="weight")
                interpolated_path.extend(self.data.transform_nodes_to_links(interpolation_nodebased)) # マルチリンクは全部追加
        #print("interpolated path: " + str(interpolated_path))

        return interpolated_path

    def _find_shortestpath_on_subgraph(self, interpolated_path):
        sub_G = self.data.network.G.edge_subgraph(self.data.get_link_index_of_G(interpolated_path))
        o = self.data.get_link_index_of_G(interpolated_path[0])[0]#[0][0]
        d = self.data.get_link_index_of_G(interpolated_path[-1])[1]#[0][1]
        length, mapmatched_nodebased = nx.single_source_dijkstra(sub_G, o, d, weight="weight")
        #print(mapmatched_nodebased)
        mapmatched_path = self.data.transform_nodes_to_links(mapmatched_nodebased)
        #print("mapmatched path: " + str(mapmatched_path))

        return mapmatched_path