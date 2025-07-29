
from scmcp_shared.server import BaseMCPManager
from scmcp_shared.server import ScanpyIOMCP
from scmcp_shared.server import ScanpyPreprocessingMCP
from scmcp_shared.server import ScanpyToolsMCP
from scmcp_shared.server import ScanpyPlottingMCP
from .util import ul_mcp



class ScanpyMCPManager(BaseMCPManager):
    """Manager class for Scanpy MCP modules."""
    
    def _init_modules(self):
        """Initialize available Scanpy MCP modules."""
        self.available_modules = {
            "io": ScanpyIOMCP().mcp,
            "pp": ScanpyPreprocessingMCP().mcp,
            "tl": ScanpyToolsMCP().mcp,
            "pl": ScanpyPlottingMCP().mcp,
            "ul": ul_mcp
        }
