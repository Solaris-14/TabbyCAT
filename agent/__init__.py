"""
TabbyPatrol Deep Agent Package
Goal-Aware Desktop AI Agent powered by LangChain deepagents:
- GoalAwareAgentEngine: cognitive engine with multi-tier evaluation & fallback
- TabbyDeepAgent: LangChain DeepAgent with 4 subagents (classifier, planner, appeals_judge, coach)
- TabbyMemory: persistent state manager in memory/ (*.md files)
- FastRulePreFilter: sub-millisecond obvious-case classifier
- print_startup_banner: prints startup banner
- trace: agent trace flags and helpers
"""

from agent.memory import TabbyMemory, MEMORY_DIR
from agent.models import get_tabby_model, get_active_model_name, print_startup_banner, OfflineTabbyChatModel
from agent.prefilter import FastRulePreFilter
from agent.subagents import create_subagent_specs
from agent.deep_agent import TabbyDeepAgent
from agent.adapter import GoalAwareAgentEngine
from agent.trace import is_trace_enabled, set_trace_enabled, trace_subagent, trace_tool, trace_file_read, trace_file_write

__all__ = [
    "GoalAwareAgentEngine",
    "TabbyDeepAgent",
    "TabbyMemory",
    "FastRulePreFilter",
    "get_tabby_model",
    "get_active_model_name",
    "print_startup_banner",
    "OfflineTabbyChatModel",
    "create_subagent_specs",
    "MEMORY_DIR",
    "is_trace_enabled",
    "set_trace_enabled",
    "trace_subagent",
    "trace_tool",
    "trace_file_read",
    "trace_file_write"
]
