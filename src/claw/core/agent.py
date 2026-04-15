from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from claw.config.settings import settings
from claw.core.memory import memory
from claw.tools import ALL_TOOLS


class LongTermState(AgentState):
    """Agent 状态结构，初始值在 invoke 时传入。"""

    user_info: dict
    preferences: dict
    longterm: str


@wrap_tool_call
def handle_tool_errors(request, handler):
    """工具执行错误处理。"""
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"工具错误：请检查您的输入并重试。({str(e)})",
            tool_call_id=request.tool_call["id"]
        )


model = ChatOpenAI(
    model=settings.llm.name,
    api_key=settings.llm.api_key,
    base_url=settings.llm.url,
    max_tokens=settings.llm.max_tokens,
)

agent = create_agent(
    model,
    tools=ALL_TOOLS,
    state_schema=LongTermState,
    checkpointer=InMemorySaver(),
    middleware=[handle_tool_errors],
)


def invoke(message: str, thread_id: str = "1"):
    """便捷调用入口。"""
    return agent.invoke(
        {
            "messages": [{"role": "user", "content": message}],
            "user_info": {
                "用户信息": memory.userprofile.user_info,
                "存储路径": memory.userprofile.user_info_path,
            },
            "preferences": {
                "用户偏好": memory.userprofile.preferences,
                "存储路径": memory.userprofile.preferences_path,
            },
            "longterm": f"用户长期记录存储目录：{memory.longterm.longterm_dir}",
        },
        {"configurable": {"thread_id": thread_id}},
    )
