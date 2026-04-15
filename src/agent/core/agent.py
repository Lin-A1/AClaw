from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI

from agent.config.settings import settings
from agent.tools import ALL_TOOLS


@wrap_tool_call
def handle_tool_errors(request, handler):
    """使用自定义消息处理工具执行错误。"""
    try:
        return handler(request)
    except Exception as e:
        # 向模型返回自定义错误消息
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
    middleware=[handle_tool_errors]
)
output = agent.invoke({"messages": [{"role": "user", "content": "帮我看看我的系统目录结构"}]})
print(output)
