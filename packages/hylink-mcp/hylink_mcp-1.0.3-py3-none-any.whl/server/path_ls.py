#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/4/27 08:29'

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from ctools import work_path

@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[dict]:
  yield {}

# 创建 MCP 服务器实例
mcp = FastMCP("path-ls-server", lifespan=server_lifespan)

@mcp.tool()
def path_ls(file_path: str = Field(description="需要查看的文件路径(默认是用户的工作路径)", default=work_path.get_user_work_path())) -> dict:
  """
  列举指定文件夹下的所有文件
  :return: 所有文件名
  """
  return os.listdir(file_path)

def main():
  mcp.run()

if __name__ == '__main__':
  main()

