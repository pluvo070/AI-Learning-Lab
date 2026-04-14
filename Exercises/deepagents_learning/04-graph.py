from typing import Annotated, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# --- [第一步] 定义 State 规格 ---
class MyAgentState(TypedDict):
    # add_messages 确保新消息是“追加”到列表，而不是覆盖列表
    messages: Annotated[list, add_messages]
    retry_count: int

# --- [第二步] 定义节点 (Node) ---
llm = ChatOpenAI(model="gpt-4o")

def node_agent(state: MyAgentState):
    """节点1: 调用 LLM"""
    print(f"\n[节点 agent] 正在处理... 当前 state 中的消息数: {len(state['messages'])}")
    # 调用 LLM，传入当前所有的历史消息
    response = llm.invoke(state["messages"])
    # 返回一个字典，框架会自动将其中的 response 加入 messages 列表
    return {"messages": [response]}

def node_counter(state: MyAgentState):
    """节点2: 纯逻辑计数"""
    print(f"[节点 counter] 正在运行... 当前重试次数: {state['retry_count']}")
    # 更新重试次数
    return {"retry_count": state["retry_count"] + 1}

# --- [第三步] 组装图并编译 ---
workflow = StateGraph(MyAgentState)

workflow.add_node("agent_node", node_agent)
workflow.add_node("counter_node", node_counter)

workflow.add_edge(START, "agent_node")       # 起点 -> LLM节点
workflow.add_edge("agent_node", "counter_node") # LLM节点 -> 计数节点
workflow.add_edge("counter_node", END)       # 计数节点 -> 终点

app = workflow.compile()

# --- [第四步] 运行 Agent ---
print("--- 启动 Agent ---")
initial_input = {
    "messages": [("user", "你好，请简单介绍一下你自己")], 
    "retry_count": 0
}
final_state = app.invoke(initial_input)

print("\n--- 运行结束 ---")
print(f"最终重试次数: {final_state['retry_count']}")
print(f"最后一条 AI 回复: {final_state['messages'][-1].content}")