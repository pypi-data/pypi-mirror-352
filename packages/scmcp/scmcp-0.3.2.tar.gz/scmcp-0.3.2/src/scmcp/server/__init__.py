
from decoupler_mcp.server import DecouplerMCPManager
from cellrank_mcp.server import CellrankMCPManager
from liana_mcp.server import LianaMCPManager
from scanpy_mcp.server import ScanpyMCPManager
from scmcp_shared.server import BaseMCPManager
from infercnv_mcp.server import InferCNVMCPManager


sc_mcp = ScanpyMCPManager("scanpy-mcp").mcp

cr_mcp = CellrankMCPManager(
    "cellrank-mcp", 
    include_modules=["pp", "kernel", "estimator", "pl"],
    include_tools={
        "pp": ["filter_and_normalize"],
        "pl": ["kernel_projection", "circular_projection"]
    }
).mcp
dc_mcp = DecouplerMCPManager(
    "decoupler-mcp", 
    include_modules=["if"],
).mcp
cnv_mcp = InferCNVMCPManager(
    "infercnv-mcp", 
    include_modules=["tl", "pl", "ul"],
    include_tools={
        "pl": ["chromosome_heatmap"],
        "tl": ["infercnv", "cnv_score"],
        "ul": ["load_gene_position"]
    }
).mcp

li_mcp = LianaMCPManager(
    "liana-mcp", include_modules=["ccc", "pl"],
    include_tools={
        "ccc": ["communicate", "rank_aggregate", "ls_ccc_method"],
        "pl": ["ccc_dotplot", "circle_plot"]
    }
).mcp


available_modules = {
    "sc": sc_mcp, 
    "li": li_mcp, 
    "cr": cr_mcp, 
    "dc": dc_mcp,
    "cnv": cnv_mcp
}


class SCMCPManager(BaseMCPManager):
    """Manager class for SCMCP modules."""
    
    def _init_modules(self):
        """Initialize available SCMCP modules."""
        self.available_modules = available_modules
