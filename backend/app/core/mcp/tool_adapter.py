"""MCP Tool → LangChain Tool 适配器"""
from typing import Any
from langchain_core.tools import BaseTool


class MCPToolAdapter(BaseTool):
    server_name: str
    tool_def: Any
    session: Any

    @property
    def name(self) -> str:
        return f"mcp_{self.server_name}_{self.tool_def.name}"

    @property
    def description(self) -> str:
        return f"[MCP:{self.server_name}] {self.tool_def.description or ''}"

    def _run(self, **kwargs) -> str:
        raise NotImplementedError("Use async version")

    async def _arun(self, **kwargs) -> str:
        result = await self.session.call_tool(self.tool_def.name, kwargs)
        return "\n".join(
            c.text for c in result.content if hasattr(c, "text")
        )
