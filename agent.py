import os
import datetime
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from tools import search_flights, search_hotels, calculate_budget

load_dotenv()

# 1. Đọc System Prompt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
prompt_path = os.path.join(BASE_DIR, "system_prompt.txt")

with open(prompt_path, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM + Tools
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node
def agent_node(state: AgentState) -> dict:
    messages = state["messages"]
    
    # Tìm tin nhắn cuối cùng của User dựa trên thuộc tính type của Langchain
    user_input = "Không xác định"
    for msg in reversed(messages):
        if getattr(msg, "type", "") == "human":
            user_input = msg.content
            break

    # Nạp System Prompt nếu chưa có
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    # Gọi LLM
    response = llm_with_tools.invoke(messages)
    
    # Ghi log vào file text tên: log_chat.txt
    log_path = os.path.join(BASE_DIR, "log_chat.txt")

    with open(log_path, "a", encoding="utf-8") as f:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n[{now}] ==========================================\n")
        
        if getattr(messages[-1], "type", "") == "human":
            f.write(f"USER INPUT: {user_input}\n")
            
        f.write("AGENT THOUGHT:\n")
        
        if response.tool_calls:
            for tc in response.tool_calls:
                f.write(f"-> GỌI TOOL: {tc['name']} | Tham số: {tc['args']}\n")
        else:
            f.write(f"-> PHẢN HỒI: {response.content}\n")
            
        f.write("==================================================\n")

    return {"messages": [response]}


# 5. Xây dựng Graph
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile()

# 6. Chat loop
if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' hoặc 'exit' để thoát")
    print("=" * 60)

    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Đã thoát chương trình.")
            break

        print("\nTravelBuddy đang xử lý...")
        
        result = graph.invoke({"messages": [("human", user_input)]})
        
        final_msg = result["messages"][-1]
        print(f"\nTravelBuddy: {final_msg.content}")