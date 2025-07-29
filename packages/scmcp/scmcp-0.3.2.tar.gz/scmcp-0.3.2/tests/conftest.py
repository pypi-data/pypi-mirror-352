
import pytest

@pytest.fixture
def mcp():
    from scmcp.server import SCMCPManager
    mcp = SCMCPManager("scmcp").mcp
    return mcp
