"""
TabbyPatrol Agent Tools
Provides tools for session planning, todo management, and memory integration:
- manage_session_todo: create, update, and review session todos/blocks
- save_learned_site_preference: update per-site learned preferences
- get_session_context: retrieve active goal, plan, and memory context
Logs [AGENT TRACE] Tool Call when --agent-trace is enabled.
"""

from typing import Optional
from langchain_core.tools import tool

from agent.memory import TabbyMemory
from agent.trace import trace_tool

memory_store = TabbyMemory()


@tool
def manage_session_todo(action: str, task: str = "", todo_id: int = 0, status: str = "pending") -> str:
    """
    Manage session study todos and milestone blocks.
    Args:
        action: 'add' (create new item), 'update' (mark status), or 'list' (view all items)
        task: Description of the study task or block (required for 'add')
        todo_id: ID of the todo item to update (required for 'update')
        status: 'pending', 'in_progress', or 'completed'
    """
    trace_tool("manage_session_todo", f"action='{action}', task='{task}', todo_id={todo_id}, status='{status}'")
    act = action.strip().lower()
    if act == "add":
        if not task:
            return "Error: 'task' description required to add a todo."
        item = memory_store.add_todo(task, status=status)
        return f"Added todo #{item['id']}: '{item['task']}' [{item['status']}]"
    elif act == "update":
        if todo_id <= 0:
            return "Error: Valid 'todo_id' required to update status."
        success = memory_store.update_todo(todo_id, status)
        if success:
            return f"Updated todo #{todo_id} to status '{status}'."
        return f"Error: Todo #{todo_id} not found."
    elif act == "list":
        todos = memory_store.get_todos()
        if not todos:
            return "No session todos currently active."
        res = ["Current Session Todos:"]
        for t in todos:
            res.append(f" - [#{t.get('id')}] [{t.get('status', 'pending').upper()}] {t.get('task')}")
        return "\n".join(res)
    else:
        return f"Unknown action '{action}'. Use 'add', 'update', or 'list'."


@tool
def save_learned_site_preference(pattern: str, allowed: bool, reason: str) -> str:
    """
    Records a learned user preference for a site or domain pattern in memory.
    Example: save_learned_site_preference("reddit.com/r/learnpython", True, "User allowed for Python studying")
    Args:
        pattern: Domain or path substring (e.g. 'reddit.com/r/learnpython')
        allowed: True if allowed/productive, False if blocked/distraction
        reason: Justification for why this site was allowed or blocked
    """
    trace_tool("save_learned_site_preference", f"pattern='{pattern}', allowed={allowed}, reason='{reason}'")
    if not pattern:
        return "Error: pattern is required."
    memory_store.update_preference(pattern, allowed, reason)
    status_str = "ALLOWED (pass)" if allowed else "BLOCKED (pop)"
    return f"Learned preference saved: '{pattern}' is now marked {status_str}. Reason: {reason}"


@tool
def get_session_context(query: str = "all") -> str:
    """
    Retrieves active focus goal, session plan, learned site preferences, and recent appeals.
    Args:
        query: 'all', 'goal', 'plan', 'preferences', or 'appeals'
    """
    trace_tool("get_session_context", f"query='{query}'")
    q = query.strip().lower()
    if q == "goal":
        return f"Active Goal: {memory_store.get_goal()}"
    elif q == "plan":
        plan = memory_store.get_plan()
        return str(plan) if plan else "No active session plan found."
    elif q == "preferences":
        return str(memory_store.get_preferences())
    elif q == "appeals":
        return str(memory_store.get_appeals(limit=5))
    else:
        return memory_store.get_system_context_summary()
