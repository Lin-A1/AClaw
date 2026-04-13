"""MCP Tool → LangChain Tool 适配器"""
from typing import Any
from pydantic import Field
from langchain_core.tools import BaseTool


class MCPToolAdapter(BaseTool):
    """将 MCP Tool 包装为 LangChain Tool"""

    server_name: str = Field(default="", exclude=True)
    tool_def: Any = Field(default=None, exclude=True)
    session: Any = Field(default=None, exclude=True)

    def __init__(self, server_name: str, tool_def: Any, session: Any, **kwargs):
        name = f"mcp_{server_name}_{tool_def.name}"
        description = f"[MCP:{server_name}] {tool_def.description or ''}"
        super().__init__(name=name, description=description)
        self.server_name = server_name
        self.tool_def = tool_def
        self.session = session

    def _run(self, **kwargs) -> str:
        raise NotImplementedError("Use async version")

    async def _arun(self, **kwargs) -> str:
        result = await self.session.call_tool(self.tool_def.name, kwargs)
        return "\n".join(
            c.text for c in result.content if hasattr(c, "text")
        )
