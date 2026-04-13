"""内置安全检查 Hook"""
from app.core.hooks.types import HookContext, HookEvent

BLOCKED_COMMANDS = {
    "rm -rf /",
    "rm -rf ~",
    "mkfs",
    "dd if=",
    "chmod 777 /",
    ":(){ :|:& };:",
}

BLOCKED_TOOLS = {"bash", "shell", "terminal"}


async def safety_check_hook(ctx: HookContext) -> HookContext:
    if ctx.tool_name in BLOCKED_TOOLS:
        raw = str(ctx.tool_input or "")
        for pattern in BLOCKED_COMMANDS:
            if pattern in raw:
                ctx.blocked = True
                ctx.block_reason = f"安全检查阻断：检测到危险操作 `{pattern}`"
                return ctx
    return ctx
