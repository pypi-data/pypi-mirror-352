
import httpx
from mcp.server.fastmcp import FastMCP
import os
import uuid
mcp = FastMCP("Demo")

host = os.getenv("server_url","http://192.168.3.23:30012")

@mcp.tool()
async def search_knowledge_base(question: str) -> str:
    """输入检索内容，检索知识库获得相关信息

    Args:
        question: 检索内容

    Returns:
        str: 检索结果
    """
    url = f"{host}/api/v1/chat/completions"
    
    stream = False
    model = "Qwen3-30B-A3B"
    appType = "knowledge"
    chatId = str(uuid.uuid4())
    # env 参数
    systemCode = os.getenv("systemCode")
    kbIds = os.getenv("kbIds")
    if kbIds is not None:
        if kbIds == "":
            kbIds = None
        else:
            kbIds = kbIds.split(",")
    fieldIds = os.getenv("fieldIds")
    if fieldIds is not None:
        if fieldIds == "":
            fieldIds = None
        else:
            fieldIds = fieldIds.split(",")
    knowledge = os.getenv("knowledge")

    replyOrigin = 1
   
    data = {
        "question": question,
        "knowledge": knowledge,
        "stream": stream,
        "model": model,
        "appType": appType,
        "chatId": chatId,
        "systemCode": systemCode,
        "kbIds": kbIds,
        "fieldIds": fieldIds,
        "replyOrigin": replyOrigin
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        # 解析结果
        try:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return content
        except Exception as e:
            return response.text



def main():
    """Entry point for the MCP Ops Toolkit"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
   import asyncio   
   ret = asyncio.run(search_knowledge_base("人工智能的定义"))
   print(ret)