"""
Agent-Assembly-Line
"""

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

@app.get('/')
def index():
    return {
        "info": ["post request to localhost:7999/question"]
    }

@app.get('/api/info')
def info():
    return {
        "name": chain.config.name,
        "description": chain.config.description,
        "LLM": chain.config.model_name,
        "doc": chain.config.doc,
    }


@app.post("/api/question")
def question(request: RequestItem):
    prompt = request.prompt

    text = chain.do_chain(prompt)
    return { "answer" : text }

