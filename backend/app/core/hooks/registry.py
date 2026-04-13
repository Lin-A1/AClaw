"""Hook 注册表"""
import asyncio
from typing import Callable, Awaitable, TYPE_CHECKING

from app.core.hooks.types import HookEvent, HookContext

if TYPE_CHECKING:
    from app.core.hooks.types import HookContext

HookHandler = Callable[["HookContext"], Awaitable["HookContext"] | "HookContext"]


class HookRegistry:
    def __init__(self):
        self._handlers: dict[HookEvent, list[HookHandler]] = {}

    def on(self, event: HookEvent):
        def decorator(fn: HookHandler) -> HookHandler:
            self._handlers.setdefault(event, []).append(fn)
            return fn
        return decorator

    def register(self, event: HookEvent, handler: HookHandler) -> None:
        self._handlers.setdefault(event, []).append(handler)

    async def emit(self, event: HookEvent, ctx: "HookContext") -> "HookContext":
        for handler in self._handlers.get(event, []):
            result = handler(ctx)
            if asyncio.iscoroutine(result):
                ctx = await result
            else:
                ctx = result
            if ctx.blocked:
                break
        return ctx
