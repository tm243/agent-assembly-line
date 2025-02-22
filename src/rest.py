"""
Agent-Assembly-Line
"""
import os

from fastapi import FastAPI
from pydantic import BaseModel

from src.chain import *
from src.memory import *

app = FastAPI()
chain = Chain("datasource/aethelland-demo/")

class RequestItem(BaseModel):
    prompt: str

class MessageItem(BaseModel):
    message: str

class AgentSelectItem(BaseModel):
    agent: str

@app.get('/')
def index():
    return {
        "info": ["post your request to localhost:7999/question"]
    }

def get_data_sources():
    datasource_path = "datasource/"
    folders = [f.name for f in os.scandir(datasource_path) if f.is_dir()]
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
    chain = Chain("datasource/" + agent + "/")
    return {}


@app.post("/api/question")
def question(request: RequestItem):
    prompt = request.prompt

    text = chain.do_chain(prompt)
    return { "answer" : text }

