from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import os
import logging
import httpx
from dataclasses import dataclass, asdict
from typing import Any, Optional, List, Dict, Annotated
from pydantic import Field

# from .exceptions import *

# Initialize FastMCP server
mcp = FastMCP(
    "hunyuan-life",
    host="0.0.0.0",
    port=os.getenv("PORT", 8000)
)

@mcp.tool(
    description="""日历查询插件
        
    Args:
        time: 用户的搜索内容，不能为空。

    Returns:
        dict: 包含生成的查询结果的字典
    """
)
async def calendar( 
    time: str = Field(description="用户的搜索内容，不能为空。")
):
    
    api_key = os.getenv("CALENDAR_API_KEY", "")
    
    if api_key is None:
        raise ValueError("环境变量CALENDAR_API_KEY没有设置")

    headers = {
        "X-Source": "mcp-server",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }
    
    calendar_url = "http://11.151.172.188:8000/openapi/betav1/tools/hunyuan_life"

    payload = {
        "time": time
    }

    logging.info(f"日历查询插件")

    try:
        timeout = httpx.Timeout(60.0, connect=30.0)
        response = httpx.post(calendar_url, headers=headers, json=payload, timeout=timeout)
        response_json = response.json()
        if "error" in response_json:
            error_data = response_json["error"]
            return TextContent(
                type="text",
                text=str(error_data)
            )
        
        return TextContent(
            type="text",
            text=response_json["answer"]
        )
    except Exception as e:
        return TextContent(
            type="text",
            text=f"调用工具失败: {str(e)}"
        )
    

@mcp.tool(
    description="""天气查询插件
        
    Args:
        city_id: id。
        api_type: forecast15days: 天气预报15天 condition: 天气实况

    Returns:
        dict: 包含生成的查询结果的字典
    """
)
async def weather( 
    city_id: str = Field(description="city_id"),
    api_type: str = Field(description="forecast15days: 天气预报15天 condition: 天气实况")
):
    
    api_key = os.getenv("WEATHER_API_KEY", "")
    
    if api_key is None:
        raise ValueError("环境变量WEATHER_API_KEY没有设置")

    headers = {
        "X-Source": "mcp-server",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key
    }
    
    weather_url = "http://11.151.172.188:8000/openapi/betav1/tools/hunyuan_life"

    payload = {
        "city_id": city_id,
        "api_type": api_type
    }

    logging.info(f"天气查询插件")

    try:
        timeout = httpx.Timeout(60.0, connect=30.0)
        response = httpx.post(weather_url, headers=headers, json=payload, timeout=timeout)
        response_json = response.json()
        if "error" in response_json:
            error_data = response_json["error"]
            return TextContent(
                type="text",
                text=str(error_data)
            )
        
        return TextContent(
            type="text",
            text=response_json["answer"]
        )
    except Exception as e:
        return TextContent(
            type="text",
            text=f"调用工具失败: {str(e)}"
        )


def run_mcp():
    print("starting")
    if os.getenv("TYPE") == "sse":
        print("starting sse")
        mcp.run(transport="sse")
    else:
        print("starting stdio")
        mcp.run(transport="stdio")

if __name__ == '__main__':
    print("starting main")
    logging.info("开始运行hunyuan-life插件")
    run_mcp()


# CALENDAR_API_KEY 72n1tn3emdipf7xh11vefovq8gl2vewp

# WEATHER_API_KEY 6lc02s4bzkdchyxdcmfgbu7g02evbbtv
