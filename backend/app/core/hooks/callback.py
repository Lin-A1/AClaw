"""LangChain Callback 适配器"""
from langchain_core.callbacks import AsyncCallbackHandler
from app.core.hooks.registry import HookRegistry
from app.core.hooks.types import HookEvent, HookContext


class ClawCallbackHandler(AsyncCallbackHandler):
    def __init__(self, hooks: HookRegistry, session_id: str):
        self._hooks = hooks
        self._session_id = session_id

    async def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        ctx = HookContext(
            event=HookEvent.PRE_TOOL_USE,
            session_id=self._session_id,
            tool_name=serialized.get("name"),
            tool_input={"input": input_str},
        )
        await self._hooks.emit(HookEvent.PRE_TOOL_USE, ctx)

    async def on_tool_end(self, output: str, **kwargs):
        ctx = HookContext(
            event=HookEvent.POST_TOOL_USE,
            session_id=self._session_id,
            tool_output=output,
        )
        await self._hooks.emit(HookEvent.POST_TOOL_USE, ctx)

    async def on_tool_error(self, error: Exception, **kwargs):
        ctx = HookContext(
            event=HookEvent.ON_AGENT_ERROR,
            session_id=self._session_id,
            error=error,
        )
        await self._hooks.emit(HookEvent.ON_AGENT_ERROR, ctx)
