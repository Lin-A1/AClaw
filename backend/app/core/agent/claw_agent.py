"""Claw Agent 核心"""
import os
import re
import uuid
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from app.core.tools import ReadTool, WriteTool, EditTool, BashTool, GlobTool, GrepTool

from app import config
from app.core.memory.store import MemoryStore, MemoryConfig
from app.core.skills.registry import SkillRegistry
from app.core.mcp.client import MCPClient
from app.core.hooks.registry import HookRegistry
from app.core.hooks.types import HookEvent, HookContext
from app.core.hooks.builtin.safety import safety_check_hook
from app.core.hooks.builtin.logger import logger_hook
from app.core.prompt.manager import PromptManager, PromptManagerConfig
from app.core.prompt.builder import SystemPromptBuilder, PromptBuilderConfig
from app.core.cot.recorder import COTRecorder
from app.core.agent.context import AgentContext
from app.core.agent.output import AgentOutput, AgentChunk

# LLM 激活 skill 的特殊标记
_SKILL_INVOKE_RE = re.compile(r"<invoke\s+(\S+)\s*/>", re.IGNORECASE)
# 33KB 以上视为大型 skill，避免每次全量注入
_LARGE_SKILL_THRESHOLD = 30 * 1024


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
            cot_dir=paths.abs("cot", cfg_dir),
        )

    def _system_prompt(self, activated_skill: str | None = None) -> str:
        return self._prompt.build(
            session_id="",  # session_id not needed for prompt
            skills_registry=self._skills,
            activated_skill_name=activated_skill,
        )

    async def run(self, message: str, session_id: Optional[str] = None) -> AgentOutput:
        session_id = session_id or str(uuid.uuid4())
        cot = COTRecorder(session_id, self._cot_dir) if self._cfg.enable_cot else None

        await self._hooks.emit(HookEvent.PRE_AGENT_RUN, HookContext(
            event=HookEvent.PRE_AGENT_RUN,
            session_id=session_id,
        ))

        try:
            tools = await self._collect_tools()
            history = self._build_history(session_id)
            input_messages = history + [HumanMessage(content=message)]

            # 第一轮：带全量 skills 索引的系统提示词
            system_prompt = self._system_prompt()
            executor = self._build_executor(tools, system_prompt)
            result = await executor.ainvoke({"messages": input_messages})

            messages_out = result.get("messages", [])
            assistant_msgs = [m for m in messages_out if isinstance(m, AIMessage)]
            raw_response = assistant_msgs[-1].content if assistant_msgs else ""

            # 提取 thinking 并记录到 COT（非流式模式）
            if cot:
                response_text = raw_response if isinstance(raw_response, str) else ""
                for m in re.finditer(r"<think>([\s\S]*?)</think>", response_text):
                    cot.record(m.group(1).strip())
                # 去掉 <think>...</think> 后作为最终回复
                response = re.sub(r"<think>[\s\S]*?</think>", "", response_text)
            else:
                response = raw_response if isinstance(raw_response, str) else ""

            # 检测 skill 激活标记（小型 skills 直接注入，大型 skills 由 LLM 决定）
            activated = self._detect_skill_invoke(response)
            if activated:
                # 第二轮：注入被激活 skill 的完整内容
                executor2 = self._build_executor(tools, self._system_prompt(activated))
                result2 = await executor2.ainvoke({"messages": input_messages})
                messages_out2 = result2.get("messages", [])
                assistant_msgs2 = [m for m in messages_out2 if isinstance(m, AIMessage)]
                raw2 = assistant_msgs2[-1].content if assistant_msgs2 else ""
                response2 = raw2 if isinstance(raw2, str) else ""
                if cot:
                    for m in re.finditer(r"<think>([\s\S]*?)</think>", response2):
                        cot.record(m.group(1).strip())
                response = re.sub(r"<think>[\s\S]*?</think>", "", response2)

            self._memory.add_message(session_id, "human", message)
            self._memory.add_message(session_id, "assistant", response)
            if cot:
                await cot.save()

            output = AgentOutput(
                response=response,
                session_id=session_id,
                thought_steps=cot.get_steps() if cot else [],
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
        history = self._build_history(session_id)
        cot = COTRecorder(session_id, self._cot_dir) if self._cfg.enable_cot else None
        tools = await self._collect_tools()
        system_prompt = self._system_prompt()
        executor = self._build_executor(tools, system_prompt, streaming=True)
        input_messages = history + [HumanMessage(content=message)]

        full_response = ""
        # Track raw accumulated text to extract <think>...</think> incrementally
        raw_accumulated = ""
        raw_cursor = 0  # How much raw text we've already emitted as clean text
        thinking_pattern = re.compile(r"<think>([\s\S]*?)</think>")

        async for event in executor.astream_events(
            {"messages": input_messages},
            version="v2",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                text = chunk.content or ""
                if text:
                    full_response += text
                    raw_accumulated += text

                    # Extract new thinking blocks that appeared in this chunk
                    segment = raw_accumulated[raw_cursor:]
                    for m in thinking_pattern.finditer(segment):
                        thinking = m.group(1).strip()
                        if thinking:
                            if cot:
                                cot.record(thinking)
                            yield AgentChunk(type="thinking", content=thinking, session_id=session_id)

                    # Yield only the non-thinking portion as text
                    clean_so_far = thinking_pattern.sub("", raw_accumulated)
                    new_clean = clean_so_far[raw_cursor:]
                    raw_cursor = len(clean_so_far)
                    if new_clean:
                        yield AgentChunk(type="text", content=new_clean, session_id=session_id)

                # additional_kwargs.reasoning_content fallback (some providers use this)
                if hasattr(chunk, "additional_kwargs"):
                    reasoning_extra = chunk.additional_kwargs.get("reasoning_content", "")
                    if reasoning_extra:
                        if cot:
                            cot.record(reasoning_extra)
                        yield AgentChunk(type="thinking", content=reasoning_extra, session_id=session_id)

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
        if cot:
            await cot.save()

    def _detect_skill_invoke(self, text: str) -> str | None:
        """检测 LLM 输出中是否包含 <invoke skill-name/> 标记"""
        m = _SKILL_INVOKE_RE.search(text)
        if not m:
            return None
        skill_name = m.group(1).strip()
        # 验证 skill 是否存在
        skill = self._skills.get(skill_name)
        if skill and len(skill.prompt_template.encode()) < _LARGE_SKILL_THRESHOLD:
            return skill_name
        return None

    def _build_llm(self) -> ChatOpenAI:
        return ChatOpenAI(
            model=self._cfg.model_name,
            openai_api_base=self._cfg.base_url,
            openai_api_key=self._cfg.api_key,
            temperature=self._cfg.temperature,
            streaming=True,
        )

    def _build_executor(
        self, tools: list, system_prompt: str, streaming: bool = False
    ):
        return create_react_agent(
            self._llm,
            tools,
            prompt=system_prompt,
        )

    def _build_history(self, session_id: str) -> list:
        msgs = self._memory.get_history(session_id)
        return [
            HumanMessage(content=m["content"]) if m["role"] == "human"
            else AIMessage(content=m["content"])
            for m in msgs
        ]

    async def _collect_tools(self) -> list:
        tools = [
            ReadTool(),
            WriteTool(),
            EditTool(),
            BashTool(),
            GlobTool(),
            GrepTool(),
        ]
        if self._mcp:
            tools.extend(self._mcp.get_tools())
        return tools
