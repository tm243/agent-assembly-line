"""
Agent-Assembly-Line
"""
import os, re
import shutil

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.chain import *
from src.memory import *
from src.exceptions import DataLoadError, EmptyDataError

app = FastAPI()
chain = Chain("chat-demo")

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
    return {
        "name": chain.config.name,
        "description": chain.config.description,
        "LLM": chain.config.model_name,
        "doc": chain.config.doc
    }

@app.post("/api/select-agent")
def select_agent(request: AgentSelectItem):
    global chain
    agent = request.agent
    chain = Chain(agent)
    return {}

def _detect_url(prompt):
    """
    Returns True if the prompt is a URL, False otherwise.
    """
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.match(prompt)

@app.post("/api/question")
async def question(request: RequestItem):
    prompt = request.prompt

    if _detect_url(prompt):
        chain.add_url(prompt)
        prompt = "Please summarize the content of the URL in 2-3 sentences"

    text = await chain.do_chain(prompt, skip_rag=False)
    return { "answer" : text }

@app.get('/api/memory')
def memory():
    return {
        "memory": chain.get_summary_memory()
    }

@app.post("/api/upload-file")
def upload_file(file: UploadFile = File(...)):
    try:
        upload_directory = "uploads"
        os.makedirs(upload_directory, exist_ok=True)
        file_path = os.path.join(upload_directory, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        total_text_length = chain.add_data(upload_directory, file.filename)

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
    try:
        messages = chain.memory_assistant.messages
        if messages:
            return JSONResponse(content={"messages": messages}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Failed to load history. {e}"}, status_code=500)