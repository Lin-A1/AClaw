"""Claw Agent 核心"""
import uuid
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

from app import config
from app.core.memory.store import MemoryStore, MemoryConfig
from app.core.skills.registry import SkillRegistry
from app.core.mcp.client import MCPClient
from app.core.hooks.registry import HookRegistry
from app.core.hooks.types import HookEvent, HookContext
from app.core.hooks.callback import ClawCallbackHandler
from app.core.hooks.builtin.safety import safety_check_hook
from app.core.hooks.builtin.logger import logger_hook
from app.core.prompt.manager import PromptManager, PromptManagerConfig
from app.core.prompt.builder import SystemPromptBuilder, PromptBuilderConfig
from app.core.cot.recorder import COTRecorder
from app.core.agent.context import AgentContext
from app.core.agent.output import AgentOutput, AgentChunk


@dataclass
class ClawAgentConfig:
    model_name: str
    base_url: str
    api_key: str
    temperature: float = 0.7
    enable_thinking: bool = True
    max_iterations: int = 20
    language: str = "zh"
    enable_cot: bool = True


class ClawAgent:
    def __init__(
        self,
        cfg: ClawAgentConfig,
        memory: MemoryStore,
        skills: SkillRegistry,
        mcp: Optional[MCPClient],
        hooks: HookRegistry,
        prompt_builder: SystemPromptBuilder,
        cot_dir: str,
    ):
        self._cfg = cfg
        self._memory = memory
        self._skills = skills
        self._mcp = mcp
        self._hooks = hooks
        self._prompt = prompt_builder
        self._cot_dir = cot_dir
        self._llm = self._build_llm()

    @classmethod
    async def from_config(cls) -> "ClawAgent":
        llm_cfg = config.llm()
        agent_cfg = config.agent()
        paths = config.paths()
        cfg_dir = config.config_dir()

        memory = MemoryStore(MemoryConfig(
            base_dir=paths.abs("memory", cfg_dir),
            session_max_messages=agent_cfg.session_max_messages,
            flush_threshold=agent_cfg.memory_flush_threshold,
        ))

        skills = SkillRegistry()
        skills.load_from_dir(paths.abs("skills", cfg_dir))

        from app.core.mcp.loader import MCPLoader
        mcp_servers = MCPLoader().load(paths.abs("mcp", cfg_dir))
        if mcp_servers:
            mcp = MCPClient(mcp_servers)
            await mcp.start()
        else:
            mcp = None

        hooks = HookRegistry()
        hooks.register(HookEvent.PRE_TOOL_USE, safety_check_hook)
        hooks.register(HookEvent.POST_TOOL_USE, logger_hook)

        prompt_mgr = PromptManager(PromptManagerConfig(
            prompts_dir=paths.abs("prompts", cfg_dir),
            language=agent_cfg.language,
        ))
        app_cfg = config.app()
        prompt_builder = SystemPromptBuilder(
            cfg=PromptBuilderConfig(
                agent_name=app_cfg.name,
                agent_role=app_cfg.role,
                agent_description=app_cfg.description,
            ),
            prompt_mgr=prompt_mgr,
            memory=memory,
            skills_list="",
        )

        agent_config = ClawAgentConfig(
            model_name=llm_cfg.name,
            base_url=llm_cfg.url,
            api_key=llm_cfg.apikey,
            temperature=llm_cfg.params.temperature,
            enable_thinking=llm_cfg.params.enable_thinking,
            max_iterations=llm_cfg.params.max_iterations,
            language=agent_cfg.language,
            enable_cot=agent_cfg.enable_cot,
        )

        return cls(
            cfg=agent_config,
            memory=memory,
            skills=skills,
            mcp=mcp,
            hooks=hooks,
            prompt_builder=prompt_builder,
            cot_dir=paths.abs("memory", cfg_dir),
        )

    async def run(self, message: str, session_id: Optional[str] = None) -> AgentOutput:
        session_id = session_id or str(uuid.uuid4())
        ctx = await self._build_context(message, session_id)

        hook_ctx = await self._hooks.emit(HookEvent.PRE_AGENT_RUN, HookContext(
            event=HookEvent.PRE_AGENT_RUN,
            session_id=session_id,
        ))

        try:
            tools = await self._collect_tools()
            executor = self._build_executor(tools, session_id)
            history = self._build_history(session_id)

            result = await executor.ainvoke({
                "input": message,
                "chat_history": history,
            })
            response = result.get("output", "")

            self._memory.add_message(session_id, "human", message)
            self._memory.add_message(session_id, "assistant", response)

            if ctx.cot:
                await ctx.cot.save()

            output = AgentOutput(
                response=response,
                session_id=session_id,
                thought_steps=ctx.cot.get_steps() if ctx.cot else [],
            )

        except Exception as e:
            await self._hooks.emit(HookEvent.ON_AGENT_ERROR, HookContext(
                event=HookEvent.ON_AGENT_ERROR,
                session_id=session_id,
                error=e,
            ))
            output = AgentOutput(
                response="",
                session_id=session_id,
                finish_reason="error",
                error=str(e),
            )

        await self._hooks.emit(HookEvent.POST_AGENT_RUN, HookContext(
            event=HookEvent.POST_AGENT_RUN,
            session_id=session_id,
            agent_output=output,
        ))

        return output

    async def stream(
        self, message: str, session_id: Optional[str] = None
    ) -> AsyncIterator[AgentChunk]:
        session_id = session_id or str(uuid.uuid4())
        ctx = await self._build_context(message, session_id)
        tools = await self._collect_tools()
        executor = self._build_executor(tools, session_id, streaming=True)
        history = self._build_history(session_id)

        full_response = ""
        async for event in executor.astream_events(
            {"input": message, "chat_history": history},
            version="v2",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "additional_kwargs"):
                    thinking = chunk.additional_kwargs.get("reasoning_content", "")
                    if thinking:
                        if ctx.cot:
                            ctx.cot.record(thinking)
                        yield AgentChunk(
                            type="thinking",
                            content=thinking,
                            session_id=session_id,
                        )
                text = chunk.content or ""
                if text:
                    full_response += text
                    yield AgentChunk(type="text", content=text, session_id=session_id)

            elif kind == "on_tool_start":
                yield AgentChunk(
                    type="tool_call",
                    content=event["data"].get("input", ""),
                    tool_name=event["name"],
                    session_id=session_id,
                )
            elif kind == "on_tool_end":
                yield AgentChunk(
                    type="tool_result",
                    content=str(event["data"].get("output", "")),
                    tool_name=event["name"],
                    session_id=session_id,
                )

        self._memory.add_message(session_id, "human", message)
        self._memory.add_message(session_id, "assistant", full_response)
        if ctx.cot:
            await ctx.cot.save()

    def _build_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self._cfg.model_name,
            openai_api_base=self._cfg.base_url,
            openai_api_key=self._cfg.api_key,
            temperature=self._cfg.temperature,
            streaming=True,
            model_kwargs={
                "enable_thinking": self._cfg.enable_thinking,
                "reasoning_split": True,
            },
        )

    async def _build_context(self, message: str, session_id: str) -> AgentContext:
        system_prompt = self._prompt.build(session_id)
        cot = COTRecorder(session_id, self._cot_dir) if self._cfg.enable_cot else None
        return AgentContext(
            session_id=session_id,
            user_message=message,
            language=self._cfg.language,
            system_prompt=system_prompt,
            cot=cot,
        )

    async def _collect_tools(self) -> list:
        tools = list(self._skills.as_langchain_tools())
        if self._mcp:
            tools.extend(await self._mcp.get_tools())
        return tools

    def _build_executor(
        self, tools: list, session_id: str, streaming: bool = False
    ):
        callback = ClawCallbackHandler(self._hooks, session_id)
        prompt = hub.pull("hwchase17/react-chat")
        agent = create_react_agent(self._llm, tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            max_iterations=self._cfg.max_iterations,
            callbacks=[callback],
            handle_parsing_errors=True,
            verbose=False,
        )

    def _build_history(self, session_id: str) -> list:
        msgs = self._memory.get_history(session_id)
        result = []
        for m in msgs:
            if m["role"] == "human":
                result.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                result.append(AIMessage(content=m["content"]))
        return result
