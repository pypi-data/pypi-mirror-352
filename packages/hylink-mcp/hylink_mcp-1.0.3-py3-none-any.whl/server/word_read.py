#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/4/27 08:29'

from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from ctools import cword

@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[dict]:
  yield {}

# 创建 MCP 服务器实例
mcp = FastMCP("word-read-server", lifespan=server_lifespan)

@mcp.tool()
def read_word(file_path: str = Field(description="word 文件的路径(不允许使用 unicode 路径)")) -> dict:
  """
  读取 word 文件的内容
  :return: 文件的内容
  """
  return cword.read_word_file(file_path)

def main():
  mcp.run()

if __name__ == '__main__':
  main()

