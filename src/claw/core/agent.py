"""
Agent 核心定义。
仅包含模型、工具、状态的初始化，不含调用逻辑。
"""

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from claw.config.settings import settings
from claw.core.memory import memory
from claw.tools import ALL_TOOLS


class LongTermState(AgentState):
    """Agent 状态，继承 memory 模块的结构。"""

    user_info: dict = {
        "用户信息": memory.userprofile.user_info,
        "存储路径": memory.userprofile.user_info_path,
    }
    preferences: dict = {
        "用户偏好": memory.userprofile.preferences,
        "存储路径": memory.userprofile.preferences_path,
    }
    longterm: str = f"用户长期记录存储目录：{memory.longterm.longterm_dir}"


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
