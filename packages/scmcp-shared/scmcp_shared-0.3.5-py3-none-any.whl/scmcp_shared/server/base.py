import inspect
from fastmcp import FastMCP
from ..schema import AdataInfo
from ..util import filter_tools
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import asyncio
from typing import Optional, List, Any, Iterable


class BaseMCP:
    """Base class for all Scanpy MCP classes."""
    
    def __init__(self, name: str, include_tools: list = None, exclude_tools: list = None, AdataInfo = AdataInfo):
        """
        Initialize BaseMCP with optional tool filtering.
        
        Args:
            name (str): Name of the MCP server
            include_tools (list, optional): List of tool names to include. If None, all tools are included.
            exclude_tools (list, optional): List of tool names to exclude. If None, no tools are excluded.
            AdataInfo: The AdataInfo class to use for type annotations.
        """
        self.mcp = FastMCP(name)
        self.include_tools = include_tools
        self.exclude_tools = exclude_tools
        self.AdataInfo = AdataInfo
        self._register_tools()

    def _register_tools(self):
        """Register all tool methods with the FastMCP instance based on include/exclude filters"""
        # Get all methods of the class
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        
        # Filter methods that start with _tool_
        tool_methods = {
            name[6:]: method  # Remove '_tool_' prefix
            for name, method in methods
            if name.startswith('_tool_')
        }
        
        # Filter tools based on include/exclude lists
        if self.include_tools is not None:
            tool_methods = {k: v for k, v in tool_methods.items() if k in self.include_tools}
        
        if self.exclude_tools is not None:
            tool_methods = {k: v for k, v in tool_methods.items() if k not in self.exclude_tools}

        # Register filtered tools
        for tool_name, tool_method in tool_methods.items():
            # Get the function returned by the tool method
            tool_func = tool_method()
            if tool_func is not None:
                self.mcp.add_tool(tool_func, name=tool_name)


class AdataState:
    def __init__(self, add_adtypes=None):
        self.adata_dic = {"exp": {}, "activity": {}, "cnv": {}, "splicing": {}}
        if isinstance(add_adtypes, str):
            self.adata_dic[add_adtypes] = {}
        elif isinstance(add_adtypes, Iterable):
            self.adata_dic.update({adtype: {} for adtype in add_adtypes})
        self.active_id = None
        self.metadatWa = {}
        self.cr_kernel = {}
        self.cr_estimator = {}
        
    def get_adata(self, sampleid=None, adtype="exp", adinfo=None):
        if adinfo is not None:
            kwargs = adinfo.model_dump()
            sampleid = kwargs.get("sampleid", None)
            adtype = kwargs.get("adtype", "exp")
        try:
            if self.active_id is None:
                return None
            sampleid = sampleid or self.active_id
            return self.adata_dic[adtype][sampleid]
        except KeyError as e:
            raise KeyError(f"Key {e} not found in adata_dic[{adtype}].Please check the sampleid or adtype.")
        except Exception as e:
            raise Exception(f"fuck {e} {type(e)}")
    
    def set_adata(self, adata, sampleid=None, sdtype="exp", adinfo=None):
        if adinfo is not None:
            kwargs = adinfo.model_dump()
            sampleid = kwargs.get("sampleid", None)
            sdtype = kwargs.get("adtype", "exp")
        sampleid = sampleid or self.active_id
        if sdtype not in self.adata_dic:
            self.adata_dic[sdtype] = {}
        self.adata_dic[sdtype][sampleid] = adata


class BaseMCPManager:
    """Base class for MCP module management."""
    
    def __init__(self, 
        name: str, 
        include_modules: Optional[List[str]] = None, 
        exclude_modules: Optional[List[str]] = None,
        include_tools: Optional[List[str]] = None,
        exclude_tools: Optional[List[str]] = None,
    ):
        """
        Initialize BaseMCPManager with optional module filtering.
        
        Args:
            name (str): Name of the MCP server
            include_modules (List[str], optional): List of module names to include. If None, all modules are included.
            exclude_modules (List[str], optional): List of module names to exclude. If None, no modules are excluded.
            include_tools (List[str], optional): List of tool names to include. If None, all tools are included.
            exclude_tools (List[str], optional): List of tool names to exclude. If None, no tools are excluded.
        """
        self.ads = AdataState()
        self.mcp = FastMCP(name, lifespan=self.adata_lifespan)
        self.include_modules = include_modules
        self.exclude_modules = exclude_modules
        self.include_tools = include_tools
        self.exclude_tools = exclude_tools
        self.available_modules = {}
        self._init_modules()
        self._register_modules()

    def _init_modules(self):
        """Initialize available modules. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _init_modules")

    def _register_modules(self):
        """Register modules based on include/exclude filters."""
        # Filter modules based on include/exclude lists
        if self.include_modules is not None:
            self.available_modules = {k: v for k, v in self.available_modules.items() if k in self.include_modules}
        
        if self.exclude_modules is not None:
            self.available_modules = {k: v for k, v in self.available_modules.items() if k not in self.exclude_modules}

        # Register each module
        for module_name, mcpi in self.available_modules.items():
            if isinstance(mcpi, FastMCP):
                if self.include_tools is not None and module_name in self.include_tools:
                    mcpi = filter_tools(mcpi, include_tools= self.include_tools[module_name])
                if self.exclude_tools is not None and module_name in self.exclude_tools:
                    mcpi = filter_tools(mcpi, exclude_tools=self.exclude_tools[module_name])

                asyncio.run(self.mcp.import_server(module_name, mcpi))
            else:
                asyncio.run(self.mcp.import_server(module_name, mcpi().mcp))

    @asynccontextmanager
    async def adata_lifespan(self, server: FastMCP) -> AsyncIterator[Any]:
        """Context manager for AdataState lifecycle."""
        yield self.ads