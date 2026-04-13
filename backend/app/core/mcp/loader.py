"""MCP 配置加载器"""
import json
import os
from app.core.mcp.schema import MCPServerConfig


class MCPLoader:
    def load(self, mcp_dir: str) -> list[MCPServerConfig]:
        path = os.path.join(mcp_dir, "mcp.json")
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        servers = []
        for name, cfg in data.get("servers", {}).items():
            servers.append(MCPServerConfig(
                name=name,
                command=cfg.get("command", ""),
                args=cfg.get("args", []),
                env=cfg.get("env", {}),
                enabled=cfg.get("enabled", True),
            ))
        return [s for s in servers if s.enabled]
