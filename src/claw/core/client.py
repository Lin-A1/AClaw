"""
Agent 调用入口。
封装 agent.invoke，提供便捷的对话接口。
"""

from langchain_core.messages import SystemMessage

from claw.core.agent import agent


def invoke(message: str, thread_id: str = "1"):
    """便捷调用入口。"""
    return agent.invoke(
        {
            "messages": [
                SystemMessage(content="your name aclaw"),
                {"role": "user", "content": message},
            ]
        },
        {"configurable": {"thread_id": thread_id}},
    )
