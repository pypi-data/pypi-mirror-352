from typing import Optional, Union, Dict, Iterator, TypedDict, List
from mcp.client.sse import sse_client
from mcp import ClientSession
from ollama import AsyncClient


class MCPServerStdio(TypedDict):
    command: str
    args: List[str]


class MCPServerSSE(TypedDict):
    host: str


class HenauAILLM:
    """
    河南农业大学人工智能平台大模型推理补全接口封装
    """

    def __init__(self, appid: str, secret: str):
        """
        初始化接口
        :param appid: 应用唯一标识
        :param secret: 应用密钥
        """
        self.appid = appid
        self.secret = secret

        self.tools = []
        self.mcp_sessions = {}

        self.ollama_client = AsyncClient(
            host="https://oauth.henau.edu.cn/oauth2_ai_server/llm_completions/appid/nd51f865dece11bdfe/secret/09f6dd2aef714c71d8e7145c8598b6c8/style/ollama/api/chat"
        )

    def completions_v1(
        self,
        model: str,
        messages: Optional[str] = None,
        stream: bool = False,
    ) -> Union[Dict, Iterator[Dict]]:
        return self.ollama_client.chat(
            model=model, messages=messages, tools=self.tools, stream=stream
        )

    def completions(
        self, model: str, messages: Optional[str] = None, stream: bool = False
    ) -> Union[Dict, Iterator[Dict]]:
        return self.completions_v1(model, messages, stream)

    async def add_mcp_server(
        self, server_name: str, mcp_server_config: MCPServerStdio | MCPServerSSE
    ):
        if server_name in self.mcp_sessions.keys():
            print(
                "\nServer already exists. if you sure it is a new server , please rename it"
            )
            return

        if "command" in mcp_server_config.keys() and "args" in mcp_server_config.keys():
            pass
        elif "host" in mcp_server_config.keys():
            # print("SSE mode")
            self._streams_context = sse_client(url=mcp_server_config["host"])
            streams = await self._streams_context.__aenter__()
            # print("get streams")
            self._session_context = ClientSession(*streams)
            # print("get session context")
            session: ClientSession = await self._session_context.__aenter__()
            # print("get session")
            await session.initialize()
            # print("init session")
            self.mcp_sessions[server_name] = session
            # print("add session")
            response = await session.list_tools()
            # print("get tools")
            self.tools.extend(
                [
                    {
                        "type": "function",
                        "function": {
                            "name": f"{server_name}___{tool.name}",
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                    for tool in response.tools
                ]
            )
