
import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

# 1. 读取 API Key
def get_openai_key():
    # 查找 .env 文件路径
    _ = load_dotenv(find_dotenv())
    # 返回 API Key
    return os.environ['OPENAI_API_KEY']

# 2. 创建客户端
client = OpenAI(api_key=get_openai_key())


# 3. 核心函数
def get_completion(prompt: str) -> str:
    """
    输入：prompt（提示词）
    输出：模型返回的文本
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",  
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content