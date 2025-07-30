from mcp.server.fastmcp import FastMCP, Context
from .weibo import WeiboCrawler

# Initialize FastMCP server with name "Weibo"
mcp = FastMCP("Weibo")

# Create an instance of WeiboCrawler for handling Weibo API operations
crawler = WeiboCrawler()

@mcp.tool()
async def search_users(ctx: Context, keyword: str, limit: int) -> list[dict]:
    """
    Search for Weibo users based on a keyword.
    
    Args:
        ctx (Context): MCP context object
        keyword (str): Search term to find users
        limit (int): Maximum number of users to return
        
    Returns:
        list[dict]: List of dictionaries containing user information
    """
    return await crawler.search_weibo_users(keyword, limit)

@mcp.tool()
async def get_profile(uid: int, ctx: Context) -> dict:
    """
    Get a Weibo user's profile information.
    
    Args:
        ctx (Context): MCP context object
        uid (int): The unique identifier of the Weibo user

    Returns:
        dict: Dictionary containing user profile information
    """
    return await crawler.extract_weibo_profile(uid)

@mcp.tool()
async def get_feeds(ctx: Context, uid: int, limit: int) -> list[dict]:
    """
    Get a Weibo user's feeds (posts).
    
    Args:
        ctx (Context): MCP context object
        uid (int): The unique identifier of the Weibo user
        limit (int): Maximum number of feeds to return
        
    Returns:
        list[dict]: List of dictionaries containing feed information
    """
    return await crawler.extract_weibo_feeds(str(uid), limit)

@mcp.tool()
async def get_hot_search(ctx: Context, limit: int) -> list[dict]:
    """
    Get the current hot search topics on Weibo.
    
    Args:
        ctx (Context): MCP context object
        limit (int): Maximum number of hot search items to return
        
    Returns:
        list[dict]: List of dictionaries containing hot search items
    """
    return await crawler.get_host_search_list(limit)

@mcp.tool()
async def search_content(ctx: Context, keyword: str, limit: int, page: int) -> list[dict]:
    """
    Search for content on Weibo based on a keyword.
    
    Args:
    ctx (Context): MCP context object
        keyword (str): Search term to find content
        limit (int): Maximum number of results to return
        page (int): Page number for pagination
        
    Returns:
        list[dict]: List of dictionaries containing search results
    """
    return await crawler.search_weibo_content(keyword, limit, page)


if __name__ == "__main__":
    # Run the MCP server using standard input/output for communication
    mcp.run(transport='stdio')
    