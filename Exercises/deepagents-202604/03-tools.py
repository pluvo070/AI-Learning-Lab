import os
from typing import Literal # 从 typing 模块导入 Literal 类型
from tavily import TavilyClient # 导入一个联网搜索API，类似一个搜索引擎接口
                                # pip install deepagents tavily-python
from deepagents import create_deep_agent # 用于创建Agent
from langchain_core.tools import tool #用于把一个普通函数“注册”为工具（给 agent用）


# 创建 Tavily 客户端对象
# api_key 从环境变量中读取（须提前在.env 或系统中配置）
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# 1. 定义Agent可用的工具函数
def internet_search(
    query: str, # 查询内容（必须传入，字符串类型）
    max_results: int = 5, # 最多返回多少条结果（默认5条）
    topic: Literal["general", "news", "finance"] = "general",
    # topic 只能是这三个值之一（类似枚举）：
    # general（普通搜索）、news（新闻）、finance（金融）
    include_raw_content: bool = False, # 是否返回网页原始内容（True = 返回全文，False = 只返回摘要）
):
    """Run a web search"""
    # 这是函数说明（docstring），Agent 会用它来理解这个工具是干嘛的

    # 调用 Tavily 提供的 search 方法, 把参数传进去，执行真实的联网搜索
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.
You have access to an internet search tool as your primary means of gathering information.
## `internet_search`
Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

# 2. 创建Agent, 指定模型、工具、系统Prompt
agent = create_deep_agent(	
    model="openai:gpt-5.4",				# 指定模型
    tools=[internet_search],			# 绑定工具
    system_prompt=research_instructions,	# 系统Prompt
)

# 3. 运行Agent
# 输入用户输入，获得回复
result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})
# 打印输出
print(result["messages"][-1].content)


# 运作流程：
# > 1. deepagent 使用内置 `write_todos` 工具规划研究任务
# > 2. 通过调用 `internet_search` 工具进行调研以收集信息
# > 3. 使用文件系统工具（`write_file` / `read_file`）来管理上下文，offload 大模型搜索结果
# > 4. 根据需要生成子代理，将复杂子任务委托给专业的子代理。
# > 5. 综合报告 ，汇总发现，形成连贯的回应。