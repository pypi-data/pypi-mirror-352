# Add lifespan support for startup/shutdown with strong typing
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My App")


@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Dynamic user data"""
    return f"Profile data for user {user_id}"
if __name__ == "__main__":
    mcp.run()
# from fake_database import Database  # Replace with your actual DB type
#
# from mcp.server.fastmcp import Context, FastMCP
#
# # Create a named server
# mcp = FastMCP("My App")
#
# # Specify dependencies for deployment and development
# mcp = FastMCP("My App", dependencies=["pandas", "numpy"])
#
#
# @dataclass
# class AppContext:
#     db: Database
#
#
# @asynccontextmanager
# async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
#     """Manage application lifecycle with type-safe context"""
#     # Initialize on startup
#     db = await Database.connect()
#     try:
#         yield AppContext(db=db)
#     finally:
#         # Cleanup on shutdown
#         await db.disconnect()
#
#
# # Pass lifespan to server
# mcp = FastMCP("My App", lifespan=app_lifespan)
#
#
# # Access type-safe lifespan context in tools
# @mcp.tool()
# def query_db(ctx: Context) -> str:
#     """Tool that uses initialized resources"""
#     db = ctx.request_context.lifespan_context.db
#     return db.query()