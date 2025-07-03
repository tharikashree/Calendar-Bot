from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import Runnable
from typing import TypedDict, List, Union
import google.generativeai as genai
from google_calendar import create_event
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Define Gemini tool (function)
schedule_meeting_function = {
    "name": "schedule_meeting",
    "description": "Schedules a meeting at a given time and date.",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {"type": "string"},
            "time": {"type": "string"},
            "topic": {"type": "string"},
        },
        "required": [ "date", "time", "topic"]
    }
}

google_api_key = os.getenv("GEMINI_API_KEY")

if not google_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment.")

# Configure Gemini
genai.configure(api_key=google_api_key)

# Define model with tool support
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=[{"function_declarations": [schedule_meeting_function]}]
)

# Define State
MessageList = List[Union[HumanMessage, AIMessage, ToolMessage]]

class AgentState(TypedDict):
    messages: MessageList

class GeminiFunctionAgent(Runnable):
    def invoke(self, state: AgentState, config=None) -> AgentState:
        user_input = state["messages"][-1].content
        response = model.generate_content(user_input)

        content = response.candidates[0].content
        function_call = (
            content.parts[0].function_call
            if content.parts and hasattr(content.parts[0], 'function_call')
            else None
        )

        ai_msg = AIMessage(
            content=content.parts[0].text if not function_call else "",
            additional_kwargs={"function_call": function_call} if function_call else {}
        )

        return {
            "messages": state["messages"] + [ai_msg],
            "next": "tool" if function_call else "end"
        }


def tool_executor(state: AgentState) -> AgentState:
    call = state["messages"][-1].additional_kwargs.get("function_call")
    if call and call.name == "schedule_meeting":
        result = create_event(**call.args)
        return {
            "messages": state["messages"] + [
                ToolMessage(
                    name=call.name,
                    content=str(result),
                    tool_call_id=getattr(call, "tool_call_id", "tool_call_fallback")
                )
            ],
            "next": "end"  # conversation is done after scheduling
        }
    return {"messages": state["messages"], "next": "end"}


# Build the LangGraph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("agent", GeminiFunctionAgent())
graph.add_node("tool", tool_executor)
graph.add_node("end", lambda x: x)  # ✅ Dummy finish node

# Set entry
graph.set_entry_point("agent")

# Conditional transitions
graph.add_conditional_edges(
    "agent",
    lambda state: state.get("next", "end"),
    {
        "tool": "tool",
        "end": "end"
    }
)

graph.add_conditional_edges(
    "tool",
    lambda state: state.get("next", "end"),
    {
        "agent": "agent",
        "end": "end"
    }
)

# Set finish
graph.set_finish_point("end")

# Compile
agent_executor = graph.compile()



agent_executor = graph.compile()