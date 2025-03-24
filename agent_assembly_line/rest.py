"""
Agent-Assembly-Line
"""

import os, re
import shutil

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from agent_assembly_line.agent_manager import AgentManager
from agent_assembly_line.exceptions import DataLoadError, EmptyDataError
from agent_assembly_line.memory_assistant import MemoryStrategy

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

app = FastAPI()
agent_manager = AgentManager()
agent_manager.select_agent("chat-demo", debug=True)

class RequestItem(BaseModel):
    prompt: str

class MessageItem(BaseModel):
    message: str

class AgentSelectItem(BaseModel):
    agent: str

class UploadFileItem(BaseModel):
    file: UploadFile

@app.get('/')
def index():
    return {
        "info": ["post your request to localhost:7999/question"]
    }

def get_agents():
    local_agents_path = "agents/"
    user_agents_path = os.path.expanduser("~/.local/share/agent-assembly-line/agents/")

    folders = []

    if os.path.exists(local_agents_path):
        folders.extend([f.name for f in os.scandir(local_agents_path) if f.is_dir()])

    if os.path.exists(user_agents_path):
        for f in os.scandir(user_agents_path):
            if f.is_dir():
                config_path = os.path.join(f.path, 'config.yaml')
                if os.path.exists(config_path):
                    folders.append(f.name)

    return folders

@app.get('/api/agents')
def data_sources():
    return get_agents()

@app.get('/api/info')
def info():
    agent = agent_manager.get_agent()
    return {
        "name": agent.config.name,
        "description": agent.config.description,
        "LLM": agent.config.model_name,
        "doc": agent.config.doc if agent.config.doc else agent.config.url,
        "memoryStrategy": str(agent.memory_strategy).replace("MemoryStrategy.", ""),
        "savingInterval": agent.memory_assistant.auto_save_interval_sec,
        "autoSaveMessageCount": agent.memory_assistant.auto_save_message_count,
        "memoryPrompt": agent.config.memory_prompt,
        "userUploadedFiles": ", ".join(agent.user_uploaded_files),
        "userAddedUrls": ", ".join(agent.user_added_urls)
    }

@app.post("/api/select-agent")
async def select_agent(request: AgentSelectItem):
    if request.agent != agent_manager.get_agent().agent_name:
        await agent_manager.get_agent().cleanup()
        agent_manager.get_agent().closeModels()
    agent = agent_manager.select_agent(request.agent, debug=True)
    return {}

def _detect_url(prompt):
    """
    Returns True if the prompt is a URL, False otherwise.
    """
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.match(prompt)

@app.post("/api/question")
async def question(request: RequestItem):
    agent = agent_manager.get_agent()
    prompt = request.prompt

    if _detect_url(prompt):
        sum, size = agent.add_url(prompt)
        return { "answer" : sum, "shouldUpdate" : True, "size" : size }

    text = agent.run(prompt, skip_rag=False)
    return { "answer" : text, "shouldUpdate" : False, "size" : 0 }

from fastapi import Request

@app.get("/api/stream")
async def stream(request: Request):
    agent = agent_manager.get_agent()
    prompt = request.query_params.get("prompt")

    async def event_generator():
        if _detect_url(prompt):
            summary, size = agent.add_url(prompt)
            yield f"data: {summary} {size}\n\n"
        else:
            async for response in agent.stream(prompt):
                yield f"data: {response}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get('/api/memory')
def memory():
    agent = agent_manager.get_agent()
    return {
        "memory": agent.get_summary_memory()
    }

@app.post("/api/upload-file")
def upload_file(file: UploadFile = File(...)):
    agent = agent_manager.get_agent()
    try:
        upload_directory = "uploads"
        os.makedirs(upload_directory, exist_ok=True)
        file_path = os.path.join(upload_directory, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        total_text_length = agent.add_file(upload_directory, file.filename)

    except EmptyDataError as e:
        return JSONResponse(content={"filename": file.filename, "message": e.message}, status_code=400)
    except DataLoadError as e:
        return JSONResponse(content={"filename": file.filename, "message": e.message}, status_code=500)
    except Exception as e:
        print("File upload failed:", e)
        return JSONResponse(content={"filename": file.filename, "message": f'File "{file.filename}" not added. {e}'}, status_code=500)
    return JSONResponse(content={"filename": file.filename, "message": f'File "{file.filename}" added successfully with {total_text_length} characters of text.'})

@app.get("/api/load-history")
def load_history():
    agent = agent_manager.get_agent()
    try:
        messages = agent.memory_assistant.messages
        messages_dict = []
        for message in messages:
            message_dict = message.__dict__
            if isinstance(message, HumanMessage):
                message_dict['sender'] = 'user'
            elif isinstance(message, AIMessage):
                message_dict['sender'] = 'llm'
            message_dict['text'] = message.content
            messages_dict.append(message_dict)
        return JSONResponse(content={"messages": messages_dict}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Failed to load history. {e}"}, status_code=500)