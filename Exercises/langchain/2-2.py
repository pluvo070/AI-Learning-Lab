
# 1. 导入模型类
# ChatOpenAI：LangChain封装的对话模型（底层还是调用OpenAI）
from langchain.chat_models import ChatOpenAI

# 2. 创建模型对象
chat = ChatOpenAI(temperature=0.0) # temperature=0 表示输出更稳定（不随机）

# 3. 导入提示模板类
from langchain.prompts import ChatPromptTemplate

# 4. 定义模板字符串
template_string = """把由三个反引号分隔的文本
翻译成一种{style}风格。
文本: ```{text}```
"""

# 5. 创建提示模板对象
# 把字符串变成“可复用模板”
prompt_template = ChatPromptTemplate.from_template(template_string)

# 6. 定义输入数据
customer_style = """正式普通话
用一个平静、尊敬的语气
"""
customer_email = """
嗯呐，我现在可是火冒三丈，我那个搅拌机盖子竟然飞了出去，把我厨房的墙壁都溅上了果汁！
更糟糕的是，保修条款可不包括清理我厨房的费用。
伙计，赶紧给我过来！
"""

# 7. 用模板生成消息
# 把 style 和 text 填进去
messages = prompt_template.format_messages(
    style=customer_style,
    text=customer_email
)
# messages 是一个列表（里面是 LangChain 的消息对象）
print(type(messages))
print(type(messages[0]))


# 8. 调用模型
response = chat(messages)
print(response.content) # 输出结果