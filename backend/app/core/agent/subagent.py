"""子代理封装"""
from dataclasses import dataclass
from typing import Optional
from app.core.agent.output import AgentOutput


@dataclass
class SubAgentTask:
    name: str
    instruction: str
    tools: list[str]
    context: str = ""


class SubAgent:
    """子代理 - 用于并行或专项任务分解"""

    def __init__(self, task: SubAgentTask, parent_agent: "ClawAgent"):
        self._task = task
        self._parent = parent_agent

    async def run(self) -> AgentOutput:
        all_tools = await self._parent._collect_tools()
        allowed = {t.name for t in all_tools if t.name in self._task.tools}
        tools = [t for t in all_tools if t.name in allowed]

        executor = self._parent._build_executor(tools, session_id="subagent")
        result = await executor.ainvoke({"input": self._task.instruction})
        return AgentOutput(
            response=result.get("output", ""),
            session_id="subagent",
        )
