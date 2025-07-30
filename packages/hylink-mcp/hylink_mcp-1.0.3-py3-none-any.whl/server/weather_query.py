#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/4/27 08:29'

from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base


@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[dict]:
    """Manage server startup and shutdown lifecycle."""
    # Initialize resources on startup
    # db = await Database.connect()
    # try:
    #     yield {"db": db}
    # finally:
    #     # Clean up on shutdown
    #     await db.disconnect()
    yield {}

# Create an MCP server
mcp = FastMCP("example-server", lifespan=server_lifespan)

"""
Tools let LLMs take actions through your server. Unlike resources,
tools are expected to perform computation and have side effects:
"""

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://restapi.amap.com/v3/weather/weatherInfo?key=6732e10afab0b90a2c9fea9d59b49b79&city={city}")
        print(response)
        return response.text

"""
Resources are how you expose data to LLMs. They're similar to GET endpoints in a REST API
- they provide data but shouldn't perform significant computation or have side effects:
"""

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Dynamic user data"""
    return f"Profile data for user {user_id}"

"""
Prompts are reusable templates that help LLMs interact with your server effectively:
"""

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

def main():
  mcp.run()

if __name__ == '__main__':
  main()

