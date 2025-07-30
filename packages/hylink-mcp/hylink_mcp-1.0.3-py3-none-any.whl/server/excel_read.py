#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/4/27 08:29'

from contextlib import asynccontextmanager
from typing import AsyncIterator

import numpy as np
from ctools import cjson
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from pydantic import Field


@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[dict]:
  yield {}


# 创建 MCP 服务器实例
mcp = FastMCP("excel-read-server", lifespan=server_lifespan)


@mcp.tool()
def read_excel_paginated(file_path: str= Field(description="Excel 文件的路径(不允许使用 unicode 路径)"),
                         sheet_name: str = Field(description="需要查看的 Sheet 名称，默认为Sheet1, 可更改此参数变更查看的 sheet", default="Sheet1"),
                         page: int = Field(description="页码，从 1 开始", default=1),
                         page_size: int = Field(description="每页的行数。默认 20", default=20),
                         header_row: int = Field(description="标题行的行号，默认为 0", default=0)) -> dict:
  """
  分页读取指定的 Excel 文件和工作表，返回当前页的数据内容。
  :return: 包含列名、数据、当前页码、每页行数和总行数的字典。
  """
  import pandas as pd
  try:
    # 读取整个表格（带表头）
    df_all = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
    df_all = df_all.replace({np.nan: None})
    total_rows = df_all.shape[0]
    start = (page - 1) * page_size
    end = start + page_size
    df = df_all.iloc[start:end]
    return cjson.dumps({
      "columns": df.columns.tolist(),
      "data": df.to_dict(orient="records"),
      "page": page,
      "page_size": page_size,
      "total_rows": total_rows
    })
  except Exception as e:
    return {"error": str(e)}

def main():
  mcp.run()

if __name__ == '__main__':
  main()
