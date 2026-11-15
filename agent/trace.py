"""
TabbyPatrol Agent Tracing Subsystem
Logs subagent calls, tool calls, and file reads/writes when --agent-trace or TABBY_AGENT_TRACE=1 is enabled.
"""

import os
import sys

_AGENT_TRACE = False


def is_trace_enabled() -> bool:
    global _AGENT_TRACE
    if _AGENT_TRACE:
        return True
    if os.environ.get("TABBY_AGENT_TRACE") in ("1", "true", "True"):
        return True
    if "--agent-trace" in sys.argv:
        _AGENT_TRACE = True
        return True
    return False


def set_trace_enabled(enabled: bool = True):
    global _AGENT_TRACE
    _AGENT_TRACE = enabled
    if enabled:
        os.environ["TABBY_AGENT_TRACE"] = "1"
    else:
        os.environ.pop("TABBY_AGENT_TRACE", None)


def trace_subagent(subagent_name: str, details: str = ""):
    if is_trace_enabled():
        msg = f"[AGENT TRACE] SubAgent: {subagent_name}"
        if details:
            msg += f" | {details}"
        print(msg, flush=True)


def trace_tool(tool_name: str, args_str: str = ""):
    if is_trace_enabled():
        msg = f"[AGENT TRACE] Tool Call: {tool_name}({args_str})"
        print(msg, flush=True)


def trace_file_read(filepath: str):
    if is_trace_enabled():
        basename = os.path.basename(filepath)
        print(f"[AGENT TRACE] File Read: memory/{basename}", flush=True)


def trace_file_write(filepath: str):
    if is_trace_enabled():
        basename = os.path.basename(filepath)
        print(f"[AGENT TRACE] File Write: memory/{basename}", flush=True)
