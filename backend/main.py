# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from agent import agent_executor

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.post("/chat")
# async def chat_with_agent(request: Request):
#     data = await request.json()
#     user_input = data.get("message")
#     result = agent_executor.invoke({"input": user_input})
#     return {"response": result['input']}

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

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("message")
    inputs = {"messages": [HumanMessage(content=user_input)]}
    result = agent_executor.invoke(inputs)
    return {"reply": result["messages"][-1].content}