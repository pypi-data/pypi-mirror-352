import os
import inspect
import scanpy as sc
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from ..schema.pp import *
from ..schema import AdataInfo
from ..util import filter_args, add_op_log, forward_request, get_ads, generate_msg
from .base import BaseMCP


class ScanpyPreprocessingMCP(BaseMCP):
    def __init__(self, include_tools: list = None, exclude_tools: list = None, AdataInfo: AdataInfo = AdataInfo):
        """
        Initialize ScanpyPreprocessingMCP with optional tool filtering.
        
        Args:
            include_tools (list, optional): List of tool names to include. If None, all tools are included.
            exclude_tools (list, optional): List of tool names to exclude. If None, no tools are excluded.
            AdataInfo: The AdataInfo class to use for type annotations.
        """
        super().__init__("ScanpyMCP-PP-Server", include_tools, exclude_tools, AdataInfo)

    def _tool_subset_cells(self):
        def _subset_cells(request: SubsetCellModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """filter or subset cells based on total genes expressed counts and numbers. or values in adata.obs[obs_key]"""
            try:
                result = forward_request("subset_cells", request, adinfo)
                if result is not None:
                    return result

                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo).copy()
                func_kwargs = filter_args(request, sc.pp.filter_cells)
                if func_kwargs:
                    sc.pp.filter_cells(adata, **func_kwargs)
                    add_op_log(adata, sc.pp.filter_cells, func_kwargs, adinfo)
                # Subset based on obs (cells) criteria
                if request.obs_key is not None:
                    if request.obs_key not in adata.obs.columns:
                        raise ValueError(f"Key '{request.obs_key}' not found in adata.obs")        
                    mask = True  # Start with all cells selected
                    if request.obs_value is not None:
                        mask = mask & (adata.obs[request.obs_key] == request.obs_value)
                    if request.obs_min is not None:
                        mask = mask & (adata.obs[request.obs_key] >= request.obs_min)        
                    if request.obs_max is not None:
                        mask = mask & (adata.obs[request.obs_key] <= request.obs_max)        
                    adata = adata[mask, :]
                    add_op_log(adata, "subset_cells", 
                        {
                        "obs_key": request.obs_key, "obs_value": request.obs_value, 
                        "obs_min": request.obs_min, "obs_max": request.obs_max
                        }, adinfo
                    )
                ads.set_adata(adata, adinfo=adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _subset_cells

    def _tool_subset_genes(self):
        def _subset_genes(request: SubsetGeneModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """filter or subset genes based on number of cells or counts, or values in adata.var[var_key] or subset highly variable genes"""
            try:
                result = forward_request("pp_subset_genes", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.pp.filter_genes)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo).copy()
                if func_kwargs:
                    sc.pp.filter_genes(adata, **func_kwargs)
                    add_op_log(adata, sc.pp.filter_genes, func_kwargs, adinfo)
                if request.var_key is not None:
                    if request.var_key not in adata.var.columns:
                        raise ValueError(f"Key '{request.var_key}' not found in adata.var")
                    mask = True  # Start with all genes selected
                    if request.var_min is not None:
                        mask = mask & (adata.var[request.var_key] >= request.var_min)
                    if request.var_max is not None:
                        mask = mask & (adata.var[request.var_key] <= request.var_max)        
                    adata = adata[:, mask]
                    if request.highly_variable is not None:
                        adata = adata[:, adata.var.highly_variable]
                    add_op_log(adata, "subset_genes", 
                        {
                        "var_key": request.var_key, "var_value": request.var_value, 
                        "var_min": request.var_min, "var_max": request.var_max, "hpv":  request.highly_variable
                        }, adinfo
                    )
                ads.set_adata(adata, adinfo=adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _subset_genes

    def _tool_calculate_qc_metrics(self):
        def _calculate_qc_metrics(request: CalculateQCMetrics, adinfo: self.AdataInfo=self.AdataInfo()):
            """Calculate quality control metrics(common metrics: total counts, gene number, percentage of counts in ribosomal and mitochondrial) for AnnData."""
            try:
                result = forward_request("pp_calculate_qc_metrics", request, adinfo)
                if result is not None:
                    return result

                func_kwargs = filter_args(request, sc.pp.calculate_qc_metrics)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                func_kwargs["inplace"] = True
                try:
                    sc.pp.calculate_qc_metrics(adata, **func_kwargs)
                    add_op_log(adata, sc.pp.calculate_qc_metrics, func_kwargs, adinfo)
                except KeyError as e:
                    raise KeyError(f"Cound find {e} in adata.var")
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _calculate_qc_metrics

    def _tool_log1p(self):
        def _log1p(request: Log1PModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Logarithmize the data matrix"""
            try:
                result = forward_request("pp_log1p", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.pp.log1p)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo).copy()
                try:
                    sc.pp.log1p(adata, **func_kwargs)
                    adata.raw = adata.copy()
                    add_op_log(adata, sc.pp.log1p, func_kwargs, adinfo)
                except Exception as e:
                    raise e
                ads.set_adata(adata, adinfo=adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _log1p

    def _tool_normalize_total(self):
        def _normalize_total(request: NormalizeTotalModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Normalize counts per cell to the same total count"""
            try:
                result = forward_request("pp_normalize_total", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.pp.normalize_total)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo).copy()
                sc.pp.normalize_total(adata, **func_kwargs)
                add_op_log(adata, sc.pp.normalize_total, func_kwargs, adinfo)
                ads.set_adata(adata, adinfo=adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _normalize_total

    def _tool_highly_variable_genes(self):
        def _highly_variable_genes(request: HighlyVariableGenesModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Annotate highly variable genes"""
            try:
                result = forward_request("pp_highly_variable_genes", request, adinfo)
                if result is not None:
                    return result
                try:  
                    func_kwargs = filter_args(request, sc.pp.highly_variable_genes)
                    ads = get_ads()
                    adata = ads.get_adata(adinfo=adinfo)
                    sc.pp.highly_variable_genes(adata, **func_kwargs)
                    add_op_log(adata, sc.pp.highly_variable_genes, func_kwargs, adinfo)
                except Exception as e:
                    raise e
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _highly_variable_genes

    def _tool_regress_out(self):
        def _regress_out(request: RegressOutModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Regress out (mostly) unwanted sources of variation."""
            try:
                result = forward_request("pp_regress_out", request, adinfo)
                if result is not None:
                    return result        
                func_kwargs = filter_args(request, sc.pp.regress_out)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo).copy()
                sc.pp.regress_out(adata, **func_kwargs)
                add_op_log(adata, sc.pp.regress_out, func_kwargs, adinfo)
                ads.set_adata(adata, adinfo=adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _regress_out

    def _tool_scale(self):
        def _scale(request: ScaleModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Scale data to unit variance and zero mean"""
            try:
                result = forward_request("pp_scale", request, adinfo)
                if result is not None:
                    return result     
                func_kwargs = filter_args(request, sc.pp.scale)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo).copy()

                sc.pp.scale(adata, **func_kwargs)
                add_op_log(adata, sc.pp.scale, func_kwargs, adinfo)
         
                ads.set_adata(adata, adinfo=adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _scale

    def _tool_combat(self):
        def _combat(request: CombatModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """ComBat function for batch effect correction"""
            try:
                result = forward_request("pp_combat", request, adinfo)
                if result is not None:
                    return result        
                func_kwargs = filter_args(request, sc.pp.combat)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo).copy()

                sc.pp.combat(adata, **func_kwargs)
                add_op_log(adata, sc.pp.combat, func_kwargs, adinfo)

                ads.set_adata(adata, adinfo=adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _combat

    def _tool_scrublet(self):
        def _scrublet(request: ScrubletModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Predict doublets using Scrublet"""
            try:
                result = forward_request("pp_scrublet", request, adinfo)
                if result is not None:
                    return result          
                func_kwargs = filter_args(request, sc.pp.scrublet)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.pp.scrublet(adata, **func_kwargs)
                add_op_log(adata, sc.pp.scrublet, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _scrublet

    def _tool_neighbors(self):
        def _neighbors(request: NeighborsModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """Compute nearest neighbors distance matrix and neighborhood graph"""
            try:
                result = forward_request("pp_neighbors", request, adinfo)
                if result is not None:
                    return result
                func_kwargs = filter_args(request, sc.pp.neighbors)
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                sc.pp.neighbors(adata, **func_kwargs)
                add_op_log(adata, sc.pp.neighbors, func_kwargs, adinfo)
                return [generate_msg(adinfo, adata, ads)]
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _neighbors
