MCP 配置, env中只能以string方式存在
{
    "mcpServers":{
        "hwsoftmcp_weikb":{
            "description": "华微软件提供的知识库服务，可以通过该服务与华微软件建立的知识库进行交互，检索知识库内容，获得相关信息",
            "command": "uvx",
            "args": [
                "hwsoftmcp_weikb@0.1.4"
            ],
            "env": {
                "server_url": "http://192.168.3.23:30012",
                "systemCode":"luzhiliang-001",
                "kbIds":"",
                "fieldIds":"doc-202506040001",
                "knowledge":"背景知识"
            }
        }
    }
}