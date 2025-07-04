from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from agent_graph import agent_executor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("message")
    prev_context = body.get("context", {})  

    # Pass both user message and current context to agent
    inputs = {
        "messages": [HumanMessage(content=user_input)],
        "context": prev_context
    }

    result = agent_executor.invoke(inputs)

    return JSONResponse({
        "reply": result["messages"][-1].content,
        "context": result["context"]  
    })
