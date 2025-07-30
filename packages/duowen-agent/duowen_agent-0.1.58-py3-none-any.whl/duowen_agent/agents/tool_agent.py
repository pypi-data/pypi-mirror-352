from typing import Union, Optional, List

from duowen_agent.agents.base import BaseAgent
from duowen_agent.agents.component.classifiers import ClassifiersMulti
from duowen_agent.agents.component.merge_contexts import DetectionMergeContexts
from duowen_agent.llm import OpenAIChat, MessagesSet
from duowen_agent.llm.entity import ToolsCall
from duowen_agent.tools.base import BaseTool
from duowen_agent.tools.manager import ToolManager
from duowen_agent.tools.mcp_client import McpClient


class ToolAgent(BaseAgent):

    def __init__(
        self,
        *,
        llm: OpenAIChat,
        tools: List[BaseTool] = None,
        mcp_client: Optional[McpClient] = None,
        filter_function_list: List[str] = None,
    ):
        super().__init__()
        self.tool_manager = ToolManager(tools, filter_function_list) if tools else None
        self.mcp_client = mcp_client
        self.llm = llm
        self.filter_function_list = filter_function_list

    @property
    def tool_classifiers(self):
        if not self.tool_manager:
            self_tool_classifiers = {}
        else:
            self_tool_classifiers = self.tool_manager.tool_classifiers

        if not self.mcp_client:
            mcp_tool_classifiers = {}
        else:
            mcp_tool_classifiers = self.mcp_client.tool_classifiers

        return {
            **mcp_tool_classifiers,
            **self_tool_classifiers,
        }

    def tool_schema(self, name: str) -> dict:
        if self.tool_manager and self.tool_manager.get_tool(name):
            return {
                "type": "function",
                "function": self.tool_manager.get_tool(name).to_schema(),
            }
        if self.mcp_client and self.mcp_client.get_tool_info(name):
            _schema = self.mcp_client.get_tool_info(name)
            return {
                "type": "function",
                "function": {
                    "name": name,
                    "description": _schema.get("description", ""),
                    "parameters": _schema.get("parameters", {}),
                },
            }

    def _run(self, instruction: str | MessagesSet, **kwargs):

        if isinstance(instruction, str):
            _question = MessagesSet().add_user(instruction)
        elif isinstance(instruction, MessagesSet) and len(instruction) == 1:
            _question = instruction
        elif isinstance(instruction, MessagesSet) and len(instruction) > 1:
            _question = MessagesSet().add_user(
                DetectionMergeContexts(self.llm).run(instruction, **kwargs)
            )
            yield f"结合上下文后，重新生成问题：{_question.get_last_message().content}"
        else:
            raise ValueError("instruction must be str or MessagesSet")

        _categories = self.tool_classifiers

        _categories["simple_small_talk"] = (
            "【最后兜底方案】通用对话模型（非实时）：仅在无法使用其他工具时使用。仅适用于非实时、非专业性的闲聊对话（如哲学讨论、故事创作、通用知识问答）。"
        )

        intention = ClassifiersMulti(self.llm).run(
            question=_question,
            categories=_categories,
            sample=[("你好", "simple_small_talk")],
        )

        if len(intention) == 1 and intention[0] == "simple_small_talk":
            yield self.llm.chat(instruction)
        else:
            for i in intention:
                if i == "simple_small_talk":
                    continue

                yield f"开始调用工具：{i}"
                res = self.llm.chat(instruction, tools=[self.tool_schema(i)])
                if isinstance(res, str):
                    yield res
                elif isinstance(res, ToolsCall):
                    a, b = self.run_tool(res.tools[0].name, res.tools[0].arguments)
                    yield a

    def run_tool(self, tool_name: str, parameters: Union[str, dict]):

        if self.tool_manager and self.tool_manager.get_tool(tool_name):
            return self.tool_manager.run_tool(tool_name, parameters)
        elif self.mcp_client.get_tool_info(tool_name):
            return self.mcp_client.run_tool(tool_name, parameters), None
        else:
            return f"未知的工具调用{tool_name}", None
