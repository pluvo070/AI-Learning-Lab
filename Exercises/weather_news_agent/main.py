# pip install deepagents langchain-tavily tavily-python python-dotenv
import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent
from tools.time_tool import get_current_time

# 1. 加载 Key 
load_dotenv()

# 2. 初始化工具列表
search_tool = TavilySearch(max_results=3)
tools = [search_tool, get_current_time]

# 3. 配置会话记忆
checkpointer = MemorySaver()

# 4. 创建 Agent (StateBackend)
system_prompt = """
# ROLE: 实时资讯与气象专家
你只处理【天气、气候、防灾、时政新闻】。严禁协助任何编程、数学或非资讯任务。

# RULES (最高优先级)
1. 事实第一：严禁顺着用户说的错误前提脑补信息，必须先查证。
2. 极简输出：严禁废话，必须严格遵守 SKILL.md 中的表格和快讯格式。
3. 职业边界：拒绝所有不相关的请求。

# FEW-SHOT EXAMPLES
Q: 帮我写个排序算法。
A: 抱歉，我是资讯专家，不提供编程服务。您可以询问“近期科技算法突破”的新闻。
Q: 北京明天天气？
A: [2026-04-14] 实时数据：北京明天...（严格执行表格格式）
"""

agent = create_deep_agent(
    model="deepseek:deepseek-chat",
    tools=tools,
    system_prompt=system_prompt,
    skills=["./skills/weather_news/"], 
    checkpointer=checkpointer
)

# 5. 启动对话
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "user_1"}}
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]: break
        
        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
        )

        # --- 查看联网日志 ---
        for msg in response["messages"]: # 如果消息里包含 tool_calls，说明它正在尝试联网
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"[Agent 动作]: 正在调用工具 {msg.tool_calls[0]['name']}...")
                print(f"[搜索关键词]: {msg.tool_calls[0]['args']}")

        print(f"Agent: {response['messages'][-1].content}")