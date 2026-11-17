from mcp.server.fastmcp import FastMCP

# Creating an MCP server 
mcp = FastMCP("Demo")

# Recommended : Adding docstrings to clarify tools for model

# Adding a tool for addition 
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers and return their sum"""
    return a + b

# Adding a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Adding a simple prompt
@mcp.prompt()
def explain_addition(a: int, b: int) -> str:
    """Create a prompt asking the model to explain an addition"""
    return(
        f"use the add tool to calculate {a} + {b}, "
        "then explain the result in simple terms."
    )


# Main execution block 
if __name__ == "__main__":
    mcp.run()