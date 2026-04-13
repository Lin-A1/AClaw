"""内置日志 Hook"""
import logging
from app.core.hooks.types import HookContext

logger = logging.getLogger(__name__)


async def logger_hook(ctx: HookContext) -> HookContext:
    if ctx.tool_name:
        logger.info(f"Tool executed: {ctx.tool_name}")
    return ctx
