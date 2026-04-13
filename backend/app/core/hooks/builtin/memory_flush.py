"""内置自动记忆 flush Hook"""
from app.core.hooks.types import HookContext

async def memory_flush_hook(ctx: HookContext) -> HookContext:
    """在特定条件下自动触发记忆 flush"""
    return ctx
