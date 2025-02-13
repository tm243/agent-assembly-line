"""
Agent-Assembly-Line
"""

from fastapi import FastAPI
from pydantic import BaseModel

from chain import *

app = FastAPI()

class RequestItem(BaseModel):
    prompt: str

@app.get('/')
def index():
    return {
        "info": ["post request to localhost:7999/question"]
    }

@app.post("/question")
def askyourdoc_question(request: RequestItem):
    prompt = request.prompt
    chain = Chain("datasource/demo/")

    text = chain.do_chain(prompt)
    return { "answer" : text }

