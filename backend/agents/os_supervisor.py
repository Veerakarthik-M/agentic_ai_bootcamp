"""
Dynamic Multi-Agent Orchestrator & Supervisor for Laptop Automation.
Dispatches specialized agents (Shell, File, Vision/GUI) based on user goal,
coordinates cross-agent workflows, verifies post-step states, and handles errors dynamically.
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional

from agents.os_state import OSAutomationState, ActionRecord
from agents.os_shell_agent import OSShellAgent
from agents.os_file_agent import OSFileAgent
from agents.os_vision_agent import OSVisionAgent
from agents.os_verifier import OSVerifierAgent
from safety.os_safety import assess_shell_risk

logger = logging.getLogger("os_supervisor")

class OSSupervisor:
    def __init__(self):
        self.shell_agent = OSShellAgent()
        self.file_agent = OSFileAgent()
        self.vision_agent = OSVisionAgent()
        self.verifier = OSVerifierAgent()

    def decompose_goal(self, user_goal: str) -> Dict[str, Any]:
        """
        Decompose a high-level user goal into an ordered multi-agent plan.
        Detects required agents and action sequence.
        """
        goal_lower = user_goal.lower()
        plan: List[Dict[str, Any]] = []
        required_agents = set()

        # Pattern 1: Diagnostics / System Resource check
        if any(w in goal_lower for w in ["battery", "cpu", "resource", "ram", "memory", "specs", "health"]):
            required_agents.add("OS_Shell_Agent")
            plan.append({
                "step_id": len(plan) + 1,
                "agent": "OS_Shell_Agent",
                "description": "Inspect CPU, Memory, Disk, and Battery diagnostics",
                "action": "get_diagnostics",
                "params": {},
                "verification": {"type": "action_status"}
            })

        # Pattern 2: Process inspection or management
        if "process" in goal_lower or "list app" in goal_lower or "running" in goal_lower:
            required_agents.add("OS_Shell_Agent")
            plan.append({
                "step_id": len(plan) + 1,
                "agent": "OS_Shell_Agent",
                "description": "Query running processes matching criteria",
                "action": "list_processes",
                "params": {"limit": 10},
                "verification": {"type": "action_status"}
            })

        # Pattern 3: Launch Notepad or text editor
        if "notepad" in goal_lower and ("open" in goal_lower or "launch" in goal_lower or "start" in goal_lower or "write" in goal_lower):
            required_agents.add("OS_Shell_Agent")
            required_agents.add("OS_Vision_GUI_Agent")
            plan.append({
                "step_id": len(plan) + 1,
                "agent": "OS_Shell_Agent",
                "description": "Launch Notepad process",
                "action": "launch_app",
                "params": {"executable": "notepad.exe"},
                "verification": {
                    "type": "process_running",
                    "process_name": "notepad.exe",
                    "expected": True
                }
            })

        # Pattern 4: Screen capture / observation
        if any(w in goal_lower for w in ["screenshot", "screen", "see", "look", "observe"]):
            required_agents.add("OS_Vision_GUI_Agent")
            plan.append({
                "step_id": len(plan) + 1,
                "agent": "OS_Vision_GUI_Agent",
                "description": "Capture screen and active window context",
                "action": "observe_screen",
                "params": {"add_grid": True},
                "verification": {"type": "action_status"}
            })

        # Pattern 5: File search or organization
        if any(w in goal_lower for w in ["organize", "find file", "search file", "clean download"]):
            required_agents.add("OS_File_Agent")
            if "organize" in goal_lower:
                plan.append({
                    "step_id": len(plan) + 1,
                    "agent": "OS_File_Agent",
                    "description": "Organize target directory files by category",
                    "action": "organize_directory",
                    "params": {"directory": "."},
                    "verification": {"type": "action_status"}
                })
            else:
                plan.append({
                    "step_id": len(plan) + 1,
                    "agent": "OS_File_Agent",
                    "description": "Search directory for requested files",
                    "action": "find_files",
                    "params": {"directory": ".", "pattern": "*"},
                    "verification": {"type": "action_status"}
                })

        # Fallback if no specific template matched: shell command or generic perception
        if not plan:
            required_agents.add("OS_Shell_Agent")
            plan.append({
                "step_id": 1,
                "agent": "OS_Shell_Agent",
                "description": "Execute requested command via PowerShell",
                "action": "execute_command",
                "params": {"command": user_goal},
                "verification": {"type": "action_status"}
            })

        return {
            "plan": plan,
            "required_agents": list(required_agents)
        }

    def execute_custom_plan(self, user_goal: str, plan: Optional[List[Dict[str, Any]]] = None) -> OSAutomationState:
        """
        Executes a dynamic multi-agent plan with closed-loop verification.
        """
        task_id = str(uuid.uuid4())[:8]
        if plan is None:
            decomp = self.decompose_goal(user_goal)
            plan = decomp["plan"]
            required_agents = decomp["required_agents"]
        else:
            required_agents = list({s.get("agent") for s in plan if s.get("agent")})

        state: OSAutomationState = {
            "task_id": task_id,
            "user_goal": user_goal,
            "required_agents": required_agents,
            "plan": plan,
            "current_step_index": 0,
            "active_agent": "Supervisor",
            "actions_history": [],
            "trace_log": [],
            "risk_score": 0.0,
            "risk_level": "LOW",
            "hitl_required": False,
            "is_completed": False,
            "final_summary": ""
        }

        state["trace_log"].append({
            "timestamp": time.time(),
            "agent": "Supervisor",
            "event": "Task initiated",
            "details": f"Goal: {user_goal} | Agents selected: {', '.join(required_agents)}"
        })

        for idx, step in enumerate(plan):
            state["current_step_index"] = idx
            target_agent = step.get("agent")
            state["active_agent"] = target_agent

            state["trace_log"].append({
                "timestamp": time.time(),
                "agent": target_agent,
                "event": f"Executing Step {idx + 1}/{len(plan)}",
                "details": step.get("description", "")
            })

            # Dispatch to appropriate agent
            start_time = time.time()
            if target_agent == "OS_Shell_Agent":
                result = self.shell_agent.process_step(step, state)
            elif target_agent == "OS_File_Agent":
                result = self.file_agent.process_step(step, state)
            elif target_agent == "OS_Vision_GUI_Agent":
                result = self.vision_agent.process_step(step, state)
            else:
                result = {"status": "error", "message": f"Unsupported agent: {target_agent}"}

            # Closed-loop verification
            verification = self.verifier.verify_step_result(step, result)
            is_verified = verification.get("status") == "VERIFIED"

            # Record action
            record: ActionRecord = {
                "agent": target_agent,
                "action_type": step.get("action", "unknown"),
                "command_or_target": str(step.get("params", {})),
                "result": result,
                "status": "VERIFIED" if is_verified else "FAILED",
                "timestamp": time.time()
            }
            state["actions_history"].append(record)

            state["trace_log"].append({
                "timestamp": time.time(),
                "agent": "OS_Verifier_Agent",
                "event": f"Step {idx + 1} Verification: {verification.get('status')}",
                "details": verification.get("reason", "")
            })

            # If an action was blocked by safety policy
            if result.get("status") == "blocked":
                state["risk_score"] = 0.95
                state["risk_level"] = "CRITICAL"
                state["hitl_required"] = True
                state["error"] = result.get("message")
                state["is_completed"] = False
                state["final_summary"] = f"Workflow halted: {result.get('message')}"
                return state

        state["is_completed"] = True
        state["final_summary"] = f"Successfully orchestrated {len(plan)} steps across agents: {', '.join(required_agents)}."
        state["trace_log"].append({
            "timestamp": time.time(),
            "agent": "Supervisor",
            "event": "Workflow Completed",
            "details": state["final_summary"]
        })

        return state
