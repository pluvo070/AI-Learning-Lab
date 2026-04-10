from deepagents import create_deep_agent # 用于创建Agent
from dotenv import load_dotenv # 用于加载环境变量
load_dotenv() # 加载环境变量

# 创建一个Agent, 指定模型
agent = create_deep_agent(
    model="deepseek:deepseek-chat" 
)

# 运行Agent
while(True):
    input_text =input("\n用户消息：")
    if input_text.lower() in ["exit","quit"]:
        print("Exiting...")
        break
    # 调用Agent的invoke方法, 把输入发送给LLM, 并获取返回结果
    results = agent.invoke(
        {"messages": [{"role": "user", "content": input_text}]}
    )    

    # print(results)
    
    # 遍历模型返回的所有消息
    # results["messages"] 是一个列表，里面包含对话内容（用户 + AI）
    for message in results["messages"]:
        message.pretty_print() # 格式化打印消息