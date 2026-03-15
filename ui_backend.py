from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from main import SmartAssistant
import uvicorn

app = FastAPI()
assistant = SmartAssistant()

class UserCommand(BaseModel):
    command: str

@app.get("/")
def read_root():
    stats = assistant.security.monitor_resources()
    return {"status": "AI Assistant Online", "system_health": stats}

@app.post("/command")
def execute_command(data: UserCommand, background_tasks: BackgroundTasks):
    # Running in background to not block the UI
    background_tasks.add_task(assistant.process_command, data.command)
    return {"message": "Command received", "command": data.command}

if __name__ == "__main__":
    print("Starting AI Assistant Web UI backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
