"""
Agent-Assembly-Line
"""
import os, re
import shutil

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.agent_manager import AgentManager
from src.exceptions import DataLoadError, EmptyDataError

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

def get_data_sources():
    local_datasource_path = "datasource/"
    user_datasource_path = os.path.expanduser("~/.local/share/agent-assembly-line/agents/")

    folders = []

    if os.path.exists(local_datasource_path):
        folders.extend([f.name for f in os.scandir(local_datasource_path) if f.is_dir()])

    if os.path.exists(user_datasource_path):
        folders.extend([f.name for f in os.scandir(user_datasource_path) if f.is_dir()])

    return folders

@app.get('/api/data-sources')
def data_sources():
    return get_data_sources()

@app.get('/api/info')
def info():
    agent = agent_manager.get_agent()
    return {
        "name": agent.config.name,
        "description": agent.config.description,
        "LLM": agent.config.model_name,
        "doc": agent.config.doc if agent.config.doc else agent.config.url,
        "memory": agent.memory_strategy,
    }

@app.post("/api/select-agent")
async def select_agent(request: AgentSelectItem):
    await agent_manager.get_agent().cleanup()
    agent_manager.select_agent(request.agent)
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
        agent.add_url(prompt)
        prompt = "Please summarize the content of the URL in 2-3 sentences"

    text = agent.do_chain(prompt, skip_rag=False)
    return { "answer" : text }

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

        total_text_length = agent.add_data(upload_directory, file.filename)

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