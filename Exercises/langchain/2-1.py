
# 1. 导入工具函数
# 这个 get_completion 是对 OpenAI API 的封装函数
# 作用：发送 prompt 给大模型，并返回生成结果（字符串）
from tool import get_completion

# 2. 示例一：计算 1 + 1
# 直接把问题作为 prompt 传给模型
# 这里传入的是一个字符串（str 类型）
response1 = get_completion("1+1是什么？")
print("示例1结果：", response1) # 打印模型返回结果

# 3. 示例二：风格转换（海盗邮件 → 正式普通话）
# 定义客户邮件
customer_email = """
嗯呐，我现在可是火冒三丈，我那个搅拌机盖子竟然飞了出去，把我厨房的墙壁都溅上了果汁！
更糟糕的是，保修条款可不包括清理我厨房的费用。
伙计，赶紧给我过来！
"""

# 4. 定义输出风格（style）, 即希望模型输出的语气
style = """正式普通话 \
用一个平静、尊敬、有礼貌的语调
""" 

# 5. 构造 Prompt
prompt = f"""把由三个反引号分隔的文本\
翻译成一种{style}风格。
文本: ```{customer_email}```
"""
print("\n生成的 Prompt：") # 打印 prompt
print(prompt)


# 6. 调用模型, 把构造好的 prompt 发给模型
response2 = get_completion(prompt)

# 7. 输出结果
print("\n示例2结果：")
print(response2)