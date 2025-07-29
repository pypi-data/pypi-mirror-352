from fastmcp import FastMCP, Context
import os
import inspect
from fastmcp import FastMCP
import scanpy as sc
from fastmcp.exceptions import ToolError
from ..schema.tl import *
from ..schema import AdataInfo
from scmcp_shared.util import filter_args, add_op_log, forward_request, get_ads, generate_msg
from .base import BaseMCP


class ScanpyToolsMCP(BaseMCP):
    def __init__(self, include_tools: list = None, exclude_tools: list = None, AdataInfo: AdataInfo = AdataInfo):
        """
        Initialize ScanpyMCP with optional tool filtering.
        
        Args:
            include_tools (list, optional): List of tool names to include. If None, all tools are included.
            exclude_tools (list, optional): List of tool names to exclude. If None, no tools are excluded.
            AdataInfo: The AdataInfo class to use for type annotations.
        """
        super().__init__("ScanpyMCP-TL-Server", include_tools, exclude_tools, AdataInfo)

    def _tool_tsne(self):
        def _tsne(request: TSNEModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """t-distributed stochastic neighborhood embedding (t-SNE) for visualization"""
            try:
                result = forward_request("tl_tsne", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.tsne)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.tsne(adata, **func_kwargs)
                add_op_log(adata, sc.tl.tsne, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _tsne

    def _tool_umap(self):
        def _umap(request: UMAPModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Uniform Manifold Approximation and Projection (UMAP) for visualization"""
            try:
                result = forward_request("tl_umap", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.umap)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.umap(adata, **func_kwargs)
                add_op_log(adata, sc.tl.umap, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _umap

    def _tool_draw_graph(self):
        def _draw_graph(request: DrawGraphModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Force-directed graph drawing"""
            try:
                result = forward_request("tl_draw_graph", request, adinfo)
                if result is not None:
                    return result    
                func_kwargs = filter_args(request, sc.tl.draw_graph)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.draw_graph(adata, **func_kwargs)
                add_op_log(adata, sc.tl.draw_graph, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _draw_graph

    def _tool_diffmap(self):
        def _diffmap(request: DiffMapModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Diffusion Maps for dimensionality reduction"""
            try:
                result = forward_request("tl_diffmap", request, adinfo)
                if result is not None:
                    return result    
                func_kwargs = filter_args(request, sc.tl.diffmap)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.diffmap(adata, **func_kwargs)
                adata.obsm["X_diffmap"] = adata.obsm["X_diffmap"][:,1:]
                add_op_log(adata, sc.tl.diffmap, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _diffmap

    def _tool_embedding_density(self):  
        def _embedding_density(request: EmbeddingDensityModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Calculate the density of cells in an embedding"""
            try:
                result = forward_request("tl_embedding_density", request, adinfo)
                if result is not None:
                    return result        
                func_kwargs = filter_args(request, sc.tl.embedding_density)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.embedding_density(adata, **func_kwargs)
                add_op_log(adata, sc.tl.embedding_density, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _embedding_density

    def _tool_leiden(self):
        def _leiden(request: LeidenModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Leiden clustering algorithm for community detection"""
            try:
                result = forward_request("tl_leiden", request, adinfo)
                if result is not None:
                    return result            
                func_kwargs = filter_args(request, sc.tl.leiden)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.leiden(adata, **func_kwargs)
                add_op_log(adata, sc.tl.leiden, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _leiden

    def _tool_louvain(self):
        def _louvain(request: LouvainModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Louvain clustering algorithm for community detection"""
            try:
                result = forward_request("tl_louvain", request, adinfo)
                if result is not None:
                    return result          
                func_kwargs = filter_args(request, sc.tl.louvain)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.louvain(adata, **func_kwargs)
                add_op_log(adata, sc.tl.louvain, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _louvain

    def _tool_dendrogram(self):
        def _dendrogram(request: DendrogramModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Hierarchical clustering dendrogram"""
            try:
                result = forward_request("tl_dendrogram", request, adinfo)
                if result is not None:
                    return result        
                func_kwargs = filter_args(request, sc.tl.dendrogram)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.dendrogram(adata, **func_kwargs)
                add_op_log(adata, sc.tl.dendrogram, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _dendrogram

    def _tool_dpt(self):
        def _dpt(request: DPTModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Diffusion Pseudotime (DPT) analysis"""
            try:
                result = forward_request("tl_dpt", request, adinfo)
                if result is not None:
                    return result          
                func_kwargs = filter_args(request, sc.tl.dpt)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.dpt(adata, **func_kwargs)
                add_op_log(adata, sc.tl.dpt, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _dpt

    def _tool_paga(self):
        def _paga(request: PAGAModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Partition-based graph abstraction"""
            try:
                result = forward_request("tl_paga", request, adinfo)
                if result is not None:
                    return result         
                func_kwargs = filter_args(request, sc.tl.paga)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)    
                sc.tl.paga(adata, **func_kwargs)
                add_op_log(adata, sc.tl.paga, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _paga

    def _tool_ingest(self):
        def _ingest(request: IngestModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Map labels and embeddings from reference data to new data"""
            try:
                result = forward_request("tl_ingest", request, adinfo)
                if result is not None:
                    return result       
                func_kwargs = filter_args(request, sc.tl.ingest)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)    
                sc.tl.ingest(adata, **func_kwargs)
                add_op_log(adata, sc.tl.ingest, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _ingest

    def _tool_rank_genes_groups(self):
        def _rank_genes_groups(request: RankGenesGroupsModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Rank genes for characterizing groups, for differentially expressison analysis"""
            try:
                result = forward_request("tl_rank_genes_groups", request, adinfo)
                if result is not None:
                    return result         
                func_kwargs = filter_args(request, sc.tl.rank_genes_groups)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.rank_genes_groups(adata, **func_kwargs)
                add_op_log(adata, sc.tl.rank_genes_groups, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _rank_genes_groups

    def _tool_filter_rank_genes_groups(self):
        def _filter_rank_genes_groups(request: FilterRankGenesGroupsModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Filter out genes based on fold change and fraction of genes"""
            try:
                result = forward_request("tl_filter_rank_genes_groups", request, adinfo)
                if result is not None:
                    return result          
                func_kwargs = filter_args(request, sc.tl.filter_rank_genes_groups)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.filter_rank_genes_groups(adata, **func_kwargs)
                add_op_log(adata, sc.tl.filter_rank_genes_groups, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _filter_rank_genes_groups

    def _tool_marker_gene_overlap(self):
        def _marker_gene_overlap(request: MarkerGeneOverlapModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Calculate overlap between data-derived marker genes and reference markers"""
            try:
                result = forward_request("tl_marker_gene_overlap", request, adinfo)
                if result is not None:
                    return result         
                func_kwargs = filter_args(request, sc.tl.marker_gene_overlap)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.marker_gene_overlap(adata, **func_kwargs)
                add_op_log(adata, sc.tl.marker_gene_overlap, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _marker_gene_overlap

    def _tool_score_genes(self):
        def _score_genes(request: ScoreGenesModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Score a set of genes based on their average expression"""
            try:
                result = forward_request("tl_score_genes", request, adinfo)
                if result is not None:
                    return result       
                func_kwargs = filter_args(request, sc.tl.score_genes)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.score_genes(adata, **func_kwargs)
                add_op_log(adata, sc.tl.score_genes, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _score_genes

    def _tool_score_genes_cell_cycle(self):
        def _score_genes_cell_cycle(request: ScoreGenesCellCycleModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Score cell cycle genes and assign cell cycle phases"""
            try:
                result = forward_request("tl_score_genes_cell_cycle", request, adinfo)
                if result is not None:
                    return result       
                func_kwargs = filter_args(request, sc.tl.score_genes_cell_cycle)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.score_genes_cell_cycle(adata, **func_kwargs)
                add_op_log(adata, sc.tl.score_genes_cell_cycle, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _score_genes_cell_cycle

    def _tool_pca(self):
        def _pca(request: PCAModel=PCAModel(), adinfo: self.AdataInfo=self.AdataInfo()):
            """Compute PCA (Principal Component Analysis)."""
            try:
                result = forward_request("tl_pca", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.tl.pca)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.tl.pca(adata, **func_kwargs)
                add_op_log(adata, sc.tl.pca, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _pca
