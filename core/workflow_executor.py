"""
HAITOMAS ASSISTANT — Workflow Executor
Executes multi-step workflow plans returned by Gemini.
Each step is dispatched sequentially with error handling.
"""
import time
from core.event_bus import event_bus, EVENT_UI_UPDATE, EVENT_SPEAK, EVENT_ERROR


class WorkflowExecutor:
    """Executes ordered multi-step workflows from Gemini."""

    def __init__(self, command_router):
        self.router = command_router

    def execute(self, workflow: dict) -> str:
        """
        Execute a workflow dict with 'goal' and 'steps'.
        Returns a summary of all executed steps.
        """
        goal = workflow.get("goal", "Unknown goal")
        steps = workflow.get("steps", [])

        if not steps:
            return "Workflow has no steps to execute."

        event_bus.publish(EVENT_UI_UPDATE, {
            "text": f"🔄 WORKFLOW: {goal}\n   Steps: {len(steps)}",
            "panel": "strategy"
        })
        event_bus.publish(EVENT_SPEAK, {"text": f"Starting workflow: {goal}"})

        results = []
        for i, step in enumerate(steps):
            step_action = step.get("action", "")
            step_params = step.get("parameters", {})

            event_bus.publish(EVENT_UI_UPDATE, {
                "text": f"   ⏳ Step {i+1}/{len(steps)}: {step_action}",
                "panel": "strategy"
            })

            # Wrap step as a command for the router
            if step_action == "conversation" or step_action == "speak":
                # Ensure we pass the right data
                command_action = {
                    "type": "conversation",
                    "reply": step_params.get("reply") or step_params.get("text", "")
                }
            else:
                command_action = {
                    "type": "command",
                    "command": step_action,
                    "parameters": step_params
                }

            try:
                result = self.router.route(command_action)
                results.append(f"Step {i+1} [{step_action}]: ✅ {result}")
            except Exception as e:
                error_msg = f"Step {i+1} [{step_action}]: ❌ {e}"
                results.append(error_msg)
                event_bus.publish(EVENT_ERROR, {"message": error_msg})

            # Small delay between steps for stability
            time.sleep(0.5)

        summary = "\n".join(results)
        event_bus.publish(EVENT_UI_UPDATE, {
            "text": f"✅ WORKFLOW COMPLETE: {goal}\n{summary}",
            "panel": "strategy"
        })
        event_bus.publish(EVENT_SPEAK, {"text": f"Workflow complete: {goal}"})

        return summary
