"""
Agent 核心类。
封装模型、状态、agent 实例，对外提供 invoke 接口。
"""

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from claw.config.settings import settings
from claw.tools import ALL_TOOLS


class BaseAgent:
    """Agent 封装类。"""

    def __init__(self):
        self.model = ChatOpenAI(
            model=settings.llm.name,
            api_key=settings.llm.api_key,
            base_url=settings.llm.url,
            max_tokens=settings.llm.max_tokens,
        )

        self._checkpointer = InMemorySaver()
        self._agent = create_agent(
            self.model,
            tools=ALL_TOOLS,
            checkpointer=self._checkpointer,
            middleware=[self._handle_tool_errors],
        )

    @wrap_tool_call
    def _handle_tool_errors(self, request, handler):
        """工具执行错误处理。"""
        try:
            return handler(request)
        except Exception as e:
            return ToolMessage(
                content=f"工具错误：请检查您的输入并重试。({str(e)})",
                tool_call_id=request.tool_call["id"]
            )

    def _thread_has_history(self, thread_id: str) -> bool:
        """
        检查该 thread 是否已有历史消息。
        通过读取 checkpointer 的最新 checkpoint 来判断。
        """
        config = {"configurable": {"thread_id": thread_id}}
        checkpoint = self._checkpointer.get(config)
        if checkpoint is None:
            return False
        messages = checkpoint.get("channel_values", {}).get("messages", [])
        return len(messages) > 0

    def invoke(
            self,
            message: str,
            thread_id: str = "1",
            system_prompt: str | None = None,
    ):
        """
        调用入口。

        system_prompt 仅在该 thread 的第一轮对话时注入，
        后续轮次传入时替换原有的 SystemMessage。
        """
        config = {"configurable": {"thread_id": thread_id}}

        if system_prompt:
            checkpoint = self._checkpointer.get(config)
            if checkpoint:
                existing = checkpoint.get("channel_values", {}).get("messages", [])
                replaced = False
                new_messages = []
                for msg in existing:
                    if isinstance(msg, SystemMessage):
                        new_messages.append(SystemMessage(content=system_prompt))
                        replaced = True
                    else:
                        new_messages.append(msg)
                if not replaced:
                    new_messages.insert(0, SystemMessage(content=system_prompt))
                messages = new_messages
            else:
                messages = [SystemMessage(content=system_prompt)]
        else:
            checkpoint = self._checkpointer.get(config)
            messages = list(checkpoint.get("channel_values", {}).get("messages", [])) if checkpoint else []

        messages.append(HumanMessage(content=message))

        return self._agent.invoke(
            {"messages": messages},
            config,
        )
