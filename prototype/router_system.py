import asyncio
import re
import time
import threading
from typing import Callable, Coroutine, Any

class EventBus:
    """Central non-blocking message distributor."""
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def emit(self, event_type: str, data: Any):
        if event_type in self.subscribers:
            tasks = []
            for cb in self.subscribers[event_type]:
                if asyncio.iscoroutinefunction(cb):
                    tasks.append(cb(data))
                else:
                    loop = asyncio.get_event_loop()
                    tasks.append(loop.run_in_executor(None, cb, data))
            if tasks:
                await asyncio.gather(*tasks)

class CommandRouter:
    """Ultra-fast bypass routing for common commands."""
    def __init__(self, llm_handler: Callable):
        self.quick_commands = {
            r"open (.*)": self.handle_open_app,
            r"type (.*)": self.handle_typing,
            r"what time (.*)": self.handle_time,
            r"stop": self.handle_stop
        }
        self.llm_handler = llm_handler

    async def route(self, text: str):
        start_time = time.time()
        text = text.lower().strip()

        # 1. Tier 1: Regex Match (Sub 1ms)
        for pattern, handler in self.quick_commands.items():
            match = re.match(pattern, text)
            if match:
                result = await handler(match.groups())
                latency = (time.time() - start_time) * 1000
                print(f"[Router] Tier 1 Match Found. Latency: {latency:.2f}ms")
                return result

        # 2. Tier 2: LLM Reasoning (Fallback)
        print("[Router] No Tier 1 match. Falling back to LLM...")
        return await self.llm_handler(text)

    async def handle_open_app(self, args):
        app_name = args[0]
        return {"action": "execute", "target": "open_app", "params": [app_name]}

    async def handle_typing(self, args):
        content = args[0]
        return {"action": "execute", "target": "type_text", "params": [content]}
    
    async def handle_time(self, args):
        import datetime
        t = datetime.datetime.now().strftime("%H:%M")
        return {"action": "speak", "content": f"The time is {t}"}

    async def handle_stop(self, args):
        return {"action": "system", "command": "shutdown"}

# Mock LLM Handler
async def mock_llm_handler(text: str):
    await asyncio.sleep(0.5) # Simulate API latency
    return {"action": "speak", "content": f"I processed '{text}' using LLM reasoning."}

async def main_demo():
    bus = EventBus()
    router = CommandRouter(mock_llm_handler)

    # Example Subscriber (Automation Engine)
    async def automation_engine(data):
        print(f"[Automation] Executing: {data}")

    bus.subscribe("command_result", automation_engine)

    # Simulate User Input
    user_inputs = ["open chrome", "who are you?"]
    
    for input_text in user_inputs:
        print(f"\nUser: {input_text}")
        result = await router.route(input_text)
        await bus.emit("command_result", result)

if __name__ == "__main__":
    asyncio.run(main_demo())
