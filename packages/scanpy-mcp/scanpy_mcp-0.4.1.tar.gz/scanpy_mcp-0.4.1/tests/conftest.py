import pytest

@pytest.fixture
def mcp():
    from scanpy_mcp.server import ScanpyMCPManager
    mcp = ScanpyMCPManager("scanpy-mcp").mcp
    return mcp
