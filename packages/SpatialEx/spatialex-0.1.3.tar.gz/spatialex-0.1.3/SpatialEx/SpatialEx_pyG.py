import os
import warnings

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
from .model import Model, Regression
from .utils import create_optimizer, Compute_metrics
from . import preprocess as pp

warnings.filterwarnings("ignore")


class Train_SpatialEx:
    def __init__(self,
                 adata1,
                 adata2,
                 num_layers=2,
                 hidden_dim=512,
                 epochs=500,
                 seed=0,
                 device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                 num_heads=4,
                 weight_decay=0,
                 optimizer="adam",
                 img_batch_size=64,
                 batch_size=4096,
                 encoder="hgnn",
                 decoder="linear",
                 activation="elu",
                 lr=0.001,
                 loss_fn="mse",
                 norm="batchnorm",
                 num_neighbors=7,
                 graph_kind='spatial',
                 scale=0.363788,
                 cell_diameter=-1,
                 resolution=64,
                 scale_exp=False,
                 prune=10000,
                 num_classes=8,
                 ):
        self.adata1 = adata1.copy()
        self.adata2 = adata2.copy()
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
        self.epochs = epochs
        self.seed = seed
        self.device = device
        self.num_heads = num_heads
        self.weight_decay = weight_decay
        self.img_batch_size = img_batch_size
        self.batch_size = batch_size
        self.encoder = encoder
        self.decoder = decoder
        self.activation = activation
        self.lr = lr
        self.loss_fn = loss_fn
        self.norm = norm
        self.num_neighbors = num_neighbors
        self.graph_kind = graph_kind
        self.scale = scale
        self.cell_diameter = cell_diameter
        self.resolution = resolution
        self.scale_exp = scale_exp
        self.prune = prune
        self.num_classes = num_classes
        self.in_dim1 = self.adata1.obsm['he'].shape[1]
        self.in_dim2 = self.adata2.obsm['he'].shape[1]
        self.out_dim1 = self.adata1.n_vars
        self.out_dim2 = self.adata2.n_vars

        self.module_HA = Model(self.num_layers, self.in_dim1, self.hidden_dim, self.out_dim1, self.loss_fn, self.device)
        self.module_HB = Model(self.num_layers, self.in_dim2, self.hidden_dim, self.out_dim2, self.loss_fn, self.device)
        self.models = [self.module_HA, self.module_HB]
        self.optimizer = create_optimizer(optimizer, self.models, self.lr, self.weight_decay)

        H1 = pp.Build_hypergraph_spatial_and_HE(adata1, num_neighbors, batch_size, False, 'spatial', 'crs',
                                                device)  # 构建超图
        self.slice1_dataloader = pp.Build_dataloader(adata1, graph=H1, graph_norm='hpnn', feat_norm=False,
                                                     prune=[prune, prune], drop_last=False)
        H2 = pp.Build_hypergraph_spatial_and_HE(adata2, num_neighbors, batch_size, False, 'spatial', 'crs',
                                                device)  # 构建超图
        self.slice2_dataloader = pp.Build_dataloader(adata2, graph=H2, graph_norm='hpnn', feat_norm=False,
                                                     prune=[prune, prune], drop_last=False)

    def train(self, data_dir):
        file_path = os.path.join(data_dir, 'datasets/Human_Breast_Cancer_Rep1/cell_feature_matrix.h5')
        obs_path = os.path.join(data_dir, 'datasets/Human_Breast_Cancer_Rep1/cells.csv')
        impute_file_path = os.path.join(data_dir, 'datasets/Human_Breast_Cancer_Rep2/cell_feature_matrix.h5')
        impute_obs_path = os.path.join(data_dir, 'datasets/Human_Breast_Cancer_Rep2/cells.csv')

        pp.set_random_seed(self.seed)
        self.module_HA.train()
        self.module_HB.train()
        print('\n')
        print('=================================== Start training =========================================')
        epoch_iter = tqdm(range(self.epochs))
        for epoch in epoch_iter:
            batch_iter = zip(self.slice1_dataloader, self.slice2_dataloader)
            for data1, data2 in batch_iter:
                graph1, he1, panel_1a, selection1 = data1[0]['graph'].to(self.device), data1[0]['he'].to(self.device), \
                    data1[0]['exp'].to(self.device), data1[0]['selection']
                graph2, he2, panel_2b, selection2 = data2[0]['graph'].to(self.device), data2[0]['he'].to(self.device), \
                    data2[0]['exp'].to(self.device), data2[0]['selection']
                agg_mtx1, agg_exp1 = data1[0]['agg_mtx'].to(self.device), data1[0]['agg_exp'].to(self.device)
                agg_mtx2, agg_exp2 = data2[0]['agg_mtx'].to(self.device), data2[0]['agg_exp'].to(self.device)

                loss1, _ = self.module_HA(graph1, he1, agg_exp1, agg_mtx1, selection1)
                loss2, _ = self.module_HB(graph2, he2, agg_exp2, agg_mtx2, selection2)
                loss = loss1 + loss2
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            epoch_iter.set_description(f"#Epoch: {epoch}: train_loss: {loss.item():.2f}")

        '''========================= 测试 ========================'''
        self.module_HA.eval()
        self.module_HB.eval()
        '''PanelA1'''
        panel_1b = []
        obs_list = []
        for data in self.slice1_dataloader:
            graph, he, obs = data[0]['graph'].to(self.device), data[0]['he'].to(self.device), data[0]['obs']
            panelB1 = self.module_HB.predict(he, graph).detach().cpu().numpy()
            panel_1b.append(panelB1)
            obs_list = obs_list + obs
        panel_1b = np.vstack(panel_1b)
        panel_1b = pd.DataFrame(panel_1b)
        panel_1b.columns = self.adata1.var_names
        panel_1b['obs_name'] = obs_list
        panel_1b = panel_1b.groupby('obs_name').mean()

        adata_raw = pp.Read_Xenium(file_path, obs_path)
        adata_raw = pp.Preprocess_adata(adata_raw, cell_mRNA_cutoff=0,
                                        scale=self.scale_exp)  # 不筛除细胞， 构建slice1上的panelB的ground truth
        adata = adata_raw[panel_1b.index]
        # graph = pp.Build_graph(adata.obsm['spatial'], graph_type='radius', radius=8, apply_normalize='gaussian', type='coo')
        graph = pp.Build_graph(adata.obsm['spatial'], graph_type='knn', weighted='gaussian', apply_normalize='row',
                               type='coo')

        # gene-level
        cs_sg, cs_reduce_sg = Compute_metrics(adata.X, panel_1b.values,
                                              metric='cosine_similarity')  # 分别以单细胞、基因计算余弦相似度和均方根误差
        ssim, ssim_reduce = Compute_metrics(adata.X, panel_1b.values, metric='ssim', graph=graph)
        pcc, pcc_reduce = Compute_metrics(adata.X, panel_1b.values, metric='pcc')
        cmd, cmd_reduce = Compute_metrics(adata.X, panel_1b.values, metric='cmd')
        print('Evaluation of the Slice1 in gene-level, cosine similarity: ', cs_reduce_sg, ' ssim: ', ssim_reduce,
              ' pcc: ',
              pcc_reduce, ' cmd: ', cmd_reduce)

        '''Panel2B'''
        panel_2a = []
        obs_list = []
        for data in self.slice2_dataloader:
            graph, he, obs = data[0]['graph'].to(self.device), data[0]['he'].to(self.device), data[0]['obs']
            panel2A = self.module_HA.predict(he, graph).detach().cpu().numpy()
            panel_2a.append(panel2A)
            obs_list = obs_list + obs
        panel_2a = np.vstack(panel_2a)
        panel_2a = pd.DataFrame(panel_2a)
        panel_2a.columns = self.adata2.var_names
        panel_2a['obs_name'] = obs_list
        panel_2a = panel_2a.groupby('obs_name').mean()

        adata_raw = pp.Read_Xenium(impute_file_path, impute_obs_path)
        adata_raw = pp.Preprocess_adata(adata_raw, cell_mRNA_cutoff=0,
                                        scale=self.scale_exp)  # 不筛除细胞，构建slice2上的panelA的ground truth
        adata_slice2 = adata_raw[panel_2a.index]
        graph = pp.Build_graph(adata_slice2.obsm['spatial'], graph_type='knn', weighted='gaussian',
                               apply_normalize='row',
                               type='coo')

        # gene-level
        cs_sg, cs_reduce_sg = Compute_metrics(adata_slice2.X, panel_2a.values,
                                              metric='cosine_similarity')  # 分别以单细胞、基因计算余弦相似度和均方根误差
        ssim, ssim_reduce = Compute_metrics(adata_slice2.X, panel_2a.values, metric='ssim', graph=graph)
        pcc, pcc_reduce = Compute_metrics(adata_slice2.X, panel_2a.values, metric='pcc')
        print('Evaluation of the Slice2 in gene-level, cosine similarity: ', cs_reduce_sg, ' ssim: ', ssim_reduce,
              ' pcc: ',
              pcc_reduce, ' cmd: ', cmd_reduce)


class Train_SpatialExP:
    def __init__(self,
                 adata1,
                 adata2,
                 seed=0,
                 device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                 num_heads=4,
                 weight_decay=0,
                 optimizer="adam",
                 img_batch_size=64,
                 batch_size=4096,
                 encoder="hgnn",
                 hidden_dim=512,
                 num_layers=2,
                 activation="elu",
                 epochs=1000,
                 lr=0.001,
                 loss_fn="mse",
                 norm="batchnorm",
                 num_neighbors=7,
                 graph_kind='spatial',
                 scale=0.363788,
                 cell_diameter=-1,
                 resolution=64,
                 num_features=3000,
                 scale_exp=False,
                 prune=100000,
                 ):
        self.adata1 = adata1.copy()
        self.adata2 = adata2.copy()
        # 基础参数
        self.seed = seed
        self.device = device
        self.num_heads = num_heads
        self.weight_decay = weight_decay
        self.img_batch_size = img_batch_size
        self.batch_size = batch_size
        self.encoder = encoder
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.activation = activation
        self.epochs = epochs
        self.lr = lr
        self.loss_fn = loss_fn
        self.norm = norm

        # 空间参数
        self.num_neighbors = num_neighbors
        self.graph_kind = graph_kind
        self.scale = scale
        self.cell_diameter = cell_diameter
        self.resolution = resolution
        self.num_features = num_features
        self.scale_exp = scale_exp
        self.prune = prune

        H1 = pp.Build_hypergraph_spatial_and_HE(adata1, num_neighbors, batch_size, False, 'spatial', 'crs',
                                                device)  # 构建超图
        self.slice1_dataloader = pp.Build_dataloader(adata1, graph=H1, graph_norm='hpnn', feat_norm=False,
                                                     prune=[prune, prune], drop_last=False)
        H2 = pp.Build_hypergraph_spatial_and_HE(adata2, num_neighbors, batch_size, False, 'spatial', 'crs',
                                                device)  # 构建超图
        self.slice2_dataloader = pp.Build_dataloader(adata2, graph=H2, graph_norm='hpnn', feat_norm=False,
                                                     prune=[prune, prune], drop_last=False)

        self.in_dim1 = adata1.obsm['he'].shape[1]
        self.in_dim2 = adata2.obsm['he'].shape[1]
        self.out_dim1 = adata1.n_vars
        self.out_dim2 = adata2.n_vars

        self.module_HA = Model(self.num_layers, self.in_dim1, self.hidden_dim, self.out_dim1, self.loss_fn, self.device)
        self.module_HB = Model(self.num_layers, self.in_dim2, self.hidden_dim, self.out_dim2, self.loss_fn, self.device)
        self.rm_AB = Regression(self.out_dim1, self.out_dim2, self.out_dim2).to(self.device)
        self.rm_BA = Regression(self.out_dim2, self.out_dim1, self.out_dim1).to(self.device)
        self.models = [self.module_HA, self.module_HB, self.rm_AB, self.rm_BA]
        self.optimizer = create_optimizer(optimizer, self.models, self.lr, self.weight_decay)

    def train(self, data_dir):
        h5_path1=os.path.join(data_dir, 'datasets/Human_Breast_Cancer_Rep1/cell_feature_matrix.h5')
        obs_path1=os.path.join(data_dir, "datasets/Human_Breast_Cancer_Rep1/cells.csv")
        h5_path2=os.path.join(data_dir, 'datasets/Human_Breast_Cancer_Rep2/cell_feature_matrix.h5')
        obs_path2=os.path.join(data_dir, "datasets/Human_Breast_Cancer_Rep2/cells.csv")

        selection = pd.read_csv(os.path.join(data_dir, 'datasets/Selection_by_name.csv'), index_col=0)
        panelA = selection.index[selection['slice1']].tolist()
        panelB = selection.index[selection['slice2']].tolist()

        pp.set_random_seed(self.seed)
        self.module_HA.train()
        self.module_HB.train()
        self.rm_AB.train()
        self.rm_BA.train()
        print('\n')
        print('=================================== Start training =========================================')
        for epoch in tqdm(range(self.epochs)):
            batch_iter = zip(self.slice1_dataloader, self.slice2_dataloader)
            for data1, data2 in batch_iter:
                graph1, he1, panel_1a, selection1 = data1[0]['graph'].to(self.device), data1[0]['he'].to(self.device), \
                    data1[0]['exp'].to(self.device), data1[0]['selection']
                graph2, he2, panel_2b, selection2 = data2[0]['graph'].to(self.device), data2[0]['he'].to(self.device), \
                    data2[0]['exp'].to(self.device), data2[0]['selection']
                agg_mtx1, agg_exp1 = data1[0]['agg_mtx'].to(self.device), data1[0]['agg_exp'].to(self.device)
                agg_mtx2, agg_exp2 = data2[0]['agg_mtx'].to(self.device), data2[0]['agg_exp'].to(self.device)

                loss1, _ = self.module_HA(graph1, he1, agg_exp1, agg_mtx1, selection1)
                loss2, _ = self.module_HB(graph2, he2, agg_exp2, agg_mtx2, selection2)

                panel_2a = self.module_HA.predict(he2, graph2)
                panel_1b = self.module_HB.predict(he1, graph1)

                # Cycle GAN
                loss3, _ = self.rm_AB(panel_1a, torch.spmm(agg_mtx1, panel_1b[selection1]), agg_mtx1)
                loss4, _ = self.rm_AB(panel_2a[selection2], agg_exp2, agg_mtx2)
                loss5, _ = self.rm_BA(panel_2b, torch.spmm(agg_mtx2, panel_2a[selection2]), agg_mtx2)
                loss6, _ = self.rm_BA(panel_1b[selection1], agg_exp1, agg_mtx1)

                loss = loss1 + loss2 + loss3 + loss4 + loss5 + loss6
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

        '''========================= 测试 ========================'''
        self.module_HA.eval()
        self.module_HB.eval()
        self.rm_AB.eval()
        self.rm_BA.eval()

        '''PanelB1'''
        panel_1b = []
        obs_list = []
        for data in self.slice1_dataloader:
            graph, he, obs = data[0]['graph'].to(self.device), data[0]['he'].to(self.device), data[0]['obs']
            panelB1 = self.module_HA.predict(he, graph)
            panelB1 = self.rm_AB.predict(panelB1).detach().cpu().numpy()
            panel_1b.append(panelB1)
            obs_list = obs_list + obs
        panel_1b = np.vstack(panel_1b)
        panel_1b = pd.DataFrame(panel_1b)
        panel_1b.columns = panelB
        panel_1b['obs_name'] = obs_list
        panel_1b = panel_1b.groupby('obs_name').mean()

        adata_raw = pp.Read_Xenium(h5_path1, obs_path1)
        adata_raw = pp.Preprocess_adata(adata_raw, cell_mRNA_cutoff=0, selected_genes=panelB,
                                        scale=self.scale_exp)  # 不筛除细胞， 构建slice1上的panelB的ground truth
        adata = adata_raw[panel_1b.index]
        graph = pp.Build_graph(adata.obsm['spatial'], graph_type='knn', weighted='gaussian', apply_normalize='row',
                               type='coo')
        ssim, ssim_reduce = Compute_metrics(adata.X, panel_1b.values, metric='ssim', graph=graph)
        pcc, pcc_reduce = Compute_metrics(adata.X, panel_1b.values, metric='pcc')
        cmd, cmd_reduce = Compute_metrics(adata.X, panel_1b.values, metric='cmd')
        print('Evaluate predicted Panel B on Slice 1, ssim: ', ssim_reduce, ' pcc: ', pcc_reduce, ' cmd: ', cmd_reduce)

        '''PanelA2'''
        panel_2a = []
        obs_list = []
        for data in self.slice2_dataloader:
            graph, he, obs = data[0]['graph'].to(self.device), data[0]['he'].to(self.device), data[0]['obs']
            panel2A = self.module_HB.predict(he, graph)
            panel2A = self.rm_BA.predict(panel2A).detach().cpu().numpy()
            panel_2a.append(panel2A)
            obs_list = obs_list + obs
        panel_2a = np.vstack(panel_2a)
        panel_2a = pd.DataFrame(panel_2a)
        panel_2a.columns = panelA
        panel_2a['obs_name'] = obs_list
        panel_2a = panel_2a.groupby('obs_name').mean()

        adata_raw = pp.Read_Xenium(h5_path2, obs_path2)
        adata_raw = pp.Preprocess_adata(adata_raw, cell_mRNA_cutoff=0, selected_genes=panelA,
                                        scale=self.scale_exp)  # 不筛除细胞，构建slice2上的panelA的ground truth
        adata_slice2 = adata_raw[panel_2a.index]
        graph = pp.Build_graph(adata_slice2.obsm['spatial'], graph_type='knn', weighted='gaussian',
                               apply_normalize='row',
                               type='coo')
        ssim, ssim_reduce = Compute_metrics(adata_slice2.X, panel_2a.values, metric='ssim', graph=graph)
        pcc, pcc_reduce = Compute_metrics(adata_slice2.X, panel_2a.values, metric='pcc')
        cmd, cmd_reduce = Compute_metrics(adata_slice2.X, panel_2a.values, metric='cmd')
        print('Evaluate predicted Panel A on Slice 2, ssim: ', ssim_reduce, ' pcc: ', pcc_reduce, ' cmd: ', cmd_reduce)
