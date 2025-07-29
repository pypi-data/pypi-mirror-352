import os
import inspect
from pathlib import Path
import scanpy as sc
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from ..schema import AdataInfo
from ..schema.io import *
from ..util import filter_args, forward_request, get_ads, generate_msg
from .base import BaseMCP


class ScanpyIOMCP(BaseMCP):
    def __init__(self, include_tools: list = None, exclude_tools: list = None, AdataInfo = AdataInfo):
        """Initialize ScanpyIOMCP with optional tool filtering."""
        super().__init__("SCMCP-IO-Server", include_tools, exclude_tools, AdataInfo)

    def _tool_read(self):
        def _read(request: ReadModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """
            Read data from 10X directory or various file formats (h5ad, 10x, text files, etc.).
            """
            try:
                res = forward_request("io_read", request, adinfo)
                if res is not None:
                    return res
                kwargs = request.model_dump()
                file = Path(kwargs.get("filename", None))
                if file.is_dir():
                    kwargs["path"] = kwargs["filename"]
                    func_kwargs = filter_args(request, sc.read_10x_mtx)
                    adata = sc.read_10x_mtx(kwargs["path"], **func_kwargs)
                elif file.is_file():
                    func_kwargs = filter_args(request, sc.read)
                    adata = sc.read(**func_kwargs)
                    if not kwargs.get("first_column_obs", True):
                        adata = adata.T
                else:
                    raise FileNotFoundError(f"{kwargs['filename']} does not exist")

                ads = get_ads()
                if adinfo.sampleid is not None:
                    ads.active_id = adinfo.sampleid
                else:
                    ads.active_id = f"adata{len(ads.adata_dic[adinfo.adtype])}"
                    
                adata.layers["counts"] = adata.X
                adata.var_names_make_unique()
                adata.obs_names_make_unique()
                ads.set_adata(adata, adinfo=adinfo)
                return generate_msg(adinfo, adata, ads)
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _read

    def _tool_write(self):
        def _write(request: WriteModel, adinfo: self.AdataInfo=self.AdataInfo()):
            """save adata into a file."""
            try:
                res = forward_request("io_write", request, adinfo)
                if res is not None:
                    return res   
                ads = get_ads()
                adata = ads.get_adata(adinfo=adinfo)
                kwargs = request.model_dump()
                sc.write(kwargs["filename"], adata)
                return {"filename": kwargs["filename"], "msg": "success to save file"}
            except ToolError as e:
                raise ToolError(e)
            except Exception as e:
                if hasattr(e, '__context__') and e.__context__:
                    raise ToolError(e.__context__)
                else:
                    raise ToolError(e)
        return _write


# Create an instance of the class
io_mcp = ScanpyIOMCP().mcp