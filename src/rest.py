"""
Agent-Assembly-Line
"""

from fastapi import FastAPI
from pydantic import BaseModel

from src.chain import *
from src.memory import *

app = FastAPI()

class RequestItem(BaseModel):
    prompt: str

class MessageItem(BaseModel):
    message: str

@app.get('/')
def index():
    return {
        "info": ["post request to localhost:7999/question"]
    }

@app.post("/api/question")
def askyourdoc_question(request: RequestItem):
    prompt = request.prompt
    chain = Chain("datasource/aethelland-demo/")

    text = chain.do_chain(prompt)
    return { "answer" : text }

