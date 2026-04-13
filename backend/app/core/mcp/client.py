"""MCP 客户端"""
from typing import Optional
from langchain_core.tools import BaseTool
from app.core.mcp.schema import MCPServerConfig
from app.core.mcp.tool_adapter import MCPToolAdapter


class MCPClient:
    def __init__(self, servers: list[MCPServerConfig]):
        self._servers = servers
        self._sessions: dict[str, Any] = {}
        self._tools: list[BaseTool] = []

    async def start(self) -> None:
        for server in self._servers:
            await self._connect(server)

    async def _connect(self, server: MCPServerConfig) -> None:
        try:
            from mcp import ClientSession
            from mcp.client.stdio import stdio_client, StdioServerParameters

            params = StdioServerParameters(
                command=server.command,
                args=server.args,
                env=server.env or None,
            )
            read, write = await stdio_client(params).__aenter__()
            session = ClientSession(read, write)
            await session.initialize()
            self._sessions[server.name] = session

            result = await session.list_tools()
            for tool_def in result.tools:
                self._tools.append(MCPToolAdapter(
                    server_name=server.name,
                    tool_def=tool_def,
                    session=session,
                ))
        except ImportError:
            pass

    async def get_tools(self) -> list[BaseTool]:
        return self._tools

    async def stop(self) -> None:
        for session in self._sessions.values():
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass
        self._sessions.clear()
        self._tools.clear()
