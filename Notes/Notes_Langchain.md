# LangChain

用于构建大模型应用程序的开源框架，有Python和JavaScript两个不同版本的包。 

[Docs by LangChain](https://docs.langchain.com/oss/python/langchain/overview)

## 常用组件

- 模型（Model）：集成各种语言模型与向量模型
- 提示（Prompts）：Prompt 管理，向模型提供指令的途径
- 链（Chain）：允许你将多个组件（如语言模型、提示模板、记忆等）串联起来，形成一个工作流
- 代理（Agent）：智能组件，可以根据用户的输入自动选择和执行不同的操作
- 记忆（Memory）：保存对话历史或上下文信息，以便在后续对话中使用
- 工具（Tool）：内置的功能模块，如文本处理工具、数据查询工具等

### 模型

- **作用**：把不同的模型，统一封装成一个接口，方便更换模型而不用重构代码。
  1. **Format**（格式化）：原始数据 → 格式化成模型可以处理的形式 → 插入到一个模板问题中 → 送入模型进行处理
  2. **Predict**（预测）：接受被送进来的问题，基于这个问题进行预测输出
  3. **Parse**（生成）：预测输出 → 格式化 → 一个 JSON 对象

- **单轮对话**

  ```py
  # 1. 加载环境变量
  from dotenv import load_dotenv 
  # 读取 .env 文件，把里面的变量（比如 API Key）加载到系统环境变量中
  load_dotenv()
  
  # 2. 导入 LangChain 组件
  from langchain_openai import ChatOpenAI
  import os
  os.environ['http_proxy'] = 'http://127.0.0.1:7890'
  os.environ['https_proxy'] = 'http://127.0.0.1:7890'
  
  # 3. 创建模型
  llm = ChatOpenAI() 					  # 使用默认模型创建对象
  
  # 4. 获取回复并打印
  print(llm.model_name)				  # 打印当前使用的模型
  print(llm.invoke("你是谁").content) 	# 打印模型输出结果
  ```

  > 修改使用的模型：`llm = ChatOpenAI(model_name="gpt-4")` 

- **多轮对话**

  ```py
  from dotenv import load_dotenv
  from langchain_openai import ChatOpenAI
  import os
  os.environ['http_proxy'] = 'http://127.0.0.1:7890'
  os.environ['https_proxy'] = 'http://127.0.0.1:7890'
  load_dotenv()
  from langchain.schema import (
      AIMessage,  	# 代表AI生成的消息
      HumanMessage,   # 代表用户输入的消息
      SystemMessage   # 代表系统生成的消息或指令(指导信息,背景信息)
  )
  
  llm = ChatOpenAI()
  
  # 模拟对话场景
  messages = [ 		
      SystemMessage(content="你是langchain的课程助理。"),
      HumanMessage(content="我是学员，我叫 Tom"),
      AIMessage(content='欢迎'),  					   
      HumanMessage('我是谁,你是谁？') 	# 用户提问
  ]
  print(llm.invoke(messages).content)
  ```

### Prompt 模版

#### PromptTemplate 

可以定义输入变量和模板文本

```py
from langchain.prompts import PromptTemplate

# 创建模板
template = PromptTemplate.from_template("给我讲个关于{name}的笑话")

# 填入具体值,获得完整prompt
print(template.format(name='小明')) # 给我讲个关于小明的笑话
```

#### ChatPromptTemplate

针对聊天场景的提示模板，支持定义多个角色的消息（用户、AI 和系统）

```py
from dotenv import load_dotenv
load_dotenv()

# 1. 导入 LangChain 组件
# 导入 System / Human / AI 三种消息模板
from langchain.prompts.chat import (
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate, 
    AIMessagePromptTemplate
)
# ChatPromptTemplate 用于组合多条消息
from langchain_core.prompts import ChatPromptTemplate
# 模型
from langchain_openai import ChatOpenAI

# 2. 创建模型
llm = ChatOpenAI()

# 3. 定义对话模板
template = ChatPromptTemplate.from_messages(
    [
        # 系统角色设定
        SystemMessagePromptTemplate.from_template("你是{product}的客服助手。你的名字叫{name}"),
        # 第一轮用户输入
        HumanMessagePromptTemplate.from_template("hello 你好吗？"),
        # 模拟模型之前的回复（AI说的话）
        AIMessagePromptTemplate.from_template("我很好 谢谢!"),
        # 第二轮用户输入（变量）
        HumanMessagePromptTemplate.from_template("{query}"),
    ]
)

# 4. 填充变量, 获取完整对话
prompt = template.format_messages(
    product="AGI课堂",
    name="Bob",
    query="你是谁"
)

# 5. 调用模型
response = llm.invoke(prompt)
print(response.content) # 输出模型回答
# 我是AGI课堂的客服助手，可以帮助您解答问题和提供信息。我的名字是Bob。有什么可以帮到您的吗？
```

#### FewShotPromptTemplate

Prompt 中给出几个 QA 例子

```py
from dotenv import load_dotenv
load_dotenv()
from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

# 例子
examples = [
    {"input": "北京天气怎么样", "output": "北京市"},
    {"input": "南京下雨吗", "output": "南京市"},
    {"input": "武汉热吗", "output": "武汉市"}
]

# 例子拼装的格式
example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Input: {input}\nOutput: {output}"
)

# Prompt模板
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Input: {input}\nOutput:",  # 要放在示例后面的提示模板字符串。
    input_variables=["input"]  # 传入的变量
)

prompt = prompt.format(input="长沙多少度")

print("===Prompt===")
print(prompt)

print("===Response===")
response = llm.invoke(prompt)
print(response.content)
```

> ```
> ===Prompt===
> Input: 北京天气怎么样
> Output: 北京市
> 
> Input: 南京下雨吗
> Output: 南京市
> 
> Input: 武汉热吗
> Output: 武汉市
> 
> Input: 长沙多少度
> Output:
> ===Response===
> 长沙市
> ```

#### 从文档中加载Prompt模版

当prompt模板数据较大时，可以使用外部导入的方式进行管理和维护

- `simple_prompt.json`

  ```json
  {
      "_type": "prompt",
      "input_variables": [
          "name",
          "love"
      ],
      "template": "我的名字叫{name}，我喜欢{love}"
  }
  ```

- 使用示例

  ```py
  from langchain.prompts import load_prompt
  
  prompt = load_prompt("simple_prompt.json", encoding="utf-8")
  print(prompt.format(name="小明", love="run"))
  ```

  

### 格式化输出 OutputParser

#### 输出列表

**CommaSeparatedListOutputParser**

```py
from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate # Prompt模板
from langchain_openai import ChatOpenAI # 模型

from langchain.output_parsers import CommaSeparatedListOutputParser

# 1. 创建一个模型(使用默认模型)
llm = ChatOpenAI() 

# 2. 创建一个列表格式输出对象, 告诉模型“你要输出一个逗号分隔的列表”
output_parser = CommaSeparatedListOutputParser() 

# 3. 创建 prompt 模板
chat_prompt = ChatPromptTemplate.from_messages(
    [
        # HumanMessagePromptTemplate：表示“用户说的话”
        # {request}：用户输入
        # {format_instructions}：输出格式要求
        HumanMessagePromptTemplate.from_template("{request}\n{format_instructions}"),
    ]
)

# 4. 构造真正发送给模型的内容
# model_request 是一个“消息对象”（不是字符串）, 是准备发给模型的输入
model_request = chat_prompt.format_prompt(
    request="给我5个心情", # 用户输入
    format_instructions=output_parser.get_format_instructions() # 格式要求
) 

# 5. 调用模型, result1 是模型返回结果（包含content）
result1 = llm.invoke(model_request) # 获取回复
print(result1.content)  # 快乐，悲伤，愤怒，放松，紧张

# 6. 解析结果, result2 是 Python 列表
result2 = output_parser.parse(result1.content) # 传入解析器, 得到格式化的回答
print(result2, type(result2)) 
# ['快乐',‘悲伤',‘愤怒','放松','紧张'］<class'list'>
```

#### 输出时间

**DatetimeOutputParser**

```py
from langchain.output_parsers import DatetimeOutputParser
output_parser = DatetimeOutputParser()

llm = ChatOpenAI(model_name='gpt-3.5-turbo')

chat_prompt = ChatPromptTemplate.from_messages(
    [
        HumanMessagePromptTemplate.from_template(
            "{request}\n{format_instructions}"),
    ]
)

model_request = chat_prompt.format_prompt(
    request="中华人民共和国是什么时候成立的",
    format_instructions=output_parser.get_format_instructions()
)

result = llm.invoke(model_request)
print(output_parser.parse(result.content)) # 1949-10-01 00:00:00
```

#### 自定义输出格式

**PydanticOutputParser**：把模型输出解析为“对象”

```py
from dotenv import load_dotenv
load_dotenv()

from langchain.output_parsers import PydanticOutputParser # 解析为对象
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate # Prompt模板
from langchain_openai import ChatOpenAI # 模型
from pydantic import BaseModel, Field # Pydantic：定义数据结构（类似Java的类）

# 1. 创建模型
llm = ChatOpenAI(model_name="gpt-4")  # 其他模型如果理解不了格式可能报错

# 2. 定义数据结构：作家类
class Writer(BaseModel): # 必须继承 BaseModel 才能被解析器使用
    name: str = Field(description="name of a Writer")  # 作者名
    nationality: str = Field(description="nationality of a Writer")  # 国籍
    magnum_opus: list = Field(description="python List of discoveries")  # 代表作

# 3. 创建输出解析器：告诉 LangChain 最终输出要变成 Writer 这个对象
outputparser = PydanticOutputParser(pydantic_object=Writer)

# 4. 创建 Prompt 模板
chat_prompt = ChatPromptTemplate.from_messages(
    [HumanMessagePromptTemplate.from_template("{request}\n{format_instructions}")]
)

# 5. 构造请求
model_request = chat_prompt.format_prompt(
    request="莫言是谁？",
    format_instructions=outputparser.get_format_instructions()
)

# 8. 调用模型
result = llm.invoke(model_request)
print(result.content) # 模型原始输出（长得像JSON的字符串）
# 9. 解析为对象
parse_data = outputparser.parse(result.content)
print("\n解析后对象：", parse_data) # 打印对象
print("\n作者名：", parse_data.name) # 打印对象属性
```

> ```py
> {
>   "name": "Mo Yan",
>   "nationality": "Chinese",
>   "magnum_opus": []
> }
> name='Mo Yan' nationality='Chinese' magnum_opus=[]
> Mo Yan
> ```



### 数据加载

- **流程**：数据源 - 加载（Load） - 转换（Transform） - 嵌入（Embed） - 存储 - 检索（Retrieve）

  ```
  CSV文件
    ↓
  Loader（读取）
    ↓
  TextSplitter（切块）
    ↓
  Embedding（向量化）
    ↓
  Chroma（存储）
    ↓
  Retriever（检索）
  ```

#### 加载文档

- **加载 CSV**

  ```py
  from langchain_community.document_loaders import CSVLoader # CSV 加载器
  
  # 创建加载器
  loader = CSVLoader("data.csv", encoding="utf-8")
  # 加载数据并切分, 每一行转成一个Document对象
  pages = loader.load_and_split()
  
  print(type(pages), len(pages))  # 查看类型和数量,pages 是一个列表
  print(type(pages[0]))  # #每个元素是 Document 对象
  # <class 'langchain_core.documents.base.Document'>
  print(pages[0].page_content)  # page_content：真正的文本内容
  ```

- **加载 PDF**

  ```py
  from langchain_community.document_loaders import PyPDFLoader
  
  # pip install pypdf 需要先安装 pypdf2
  loader = PyPDFLoader("中国人工智能系列白皮书.pdf")
  pages = loader.load_and_split()
  print(pages[13].page_content)
  ```

#### 文档切割

- **按字符递归拆分**：在遇到特定字符（如换行符、空格等）时进行分割

  ```py
  from langchain.text_splitter import RecursiveCharacterTextSplitter
  from langchain_community.document_loaders import PyPDFLoader
  
  # 1. 读取 PDF 文件
  loader = PyPDFLoader("中国人工智能系列白皮书.pdf")
  # 按页加载, 每页变成一个 Document
  pages = loader.load_and_split()
  
  # 2. 创建文本切分器
  text_splitter = RecursiveCharacterTextSplitter(
      # 每个块中的最大字符数
      chunk_size=200,
      # 邻块之间的重叠字符数(确保如果重要信息横跨两个块，它不会被错过)
      chunk_overlap=50,
  )
  
  # 3. 对某一页进行切分
  # pages[13]：第14页（从0开始）
  # page_content：这一页的文本
  paragraphs = text_splitter.create_documents([pages[13].page_content])
  
  # 4. 输出切分结果
  for para in paragraphs:
      print(para.page_content) # 每一小段
      print('-------')
  ```

- **按照 token 拆分**

  基于 `tiktoken` 库进行分词和编码。`tiktoken` 通常用于处理与 OpenAI 相关的文本内容，因为它使用 OpenAI 的编码方式。

  ```py
  from langchain.text_splitter import RecursiveCharacterTextSplitter
  from langchain_community.document_loaders import PyPDFLoader
  
  loader = PyPDFLoader("中国人工智能系列白皮书.pdf")
  pages = loader.load_and_split()
  
  text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
      chunk_size=200,
      chunk_overlap=50,
  )
  texts = text_splitter.split_text(pages[13].page_content)
  print(len(texts))
  for text in texts:
      print(text)
      print('-' * 50)
  ```



### 文本向量化模型

```py
# 示例 单个文本向量化: 将文本 text 转换为其嵌入表示形式
text = 'this is a text'
# embed_query：单条文本 → 向量
embedding_text = embeddings.embed_query(text)
print("单条向量:", embedding_text)
print("维度:", len(embedding_text))
```

```py
from dotenv import load_dotenv
load_dotenv()

# 导入CSV加载器（读取数据）
from langchain_community.document_loaders import CSVLoader
# 导入向量模型（Embedding模型）
from langchain_openai import OpenAIEmbeddings 

# 1. 创建Embedding模型, 用于把文本转成向量
embeddings = OpenAIEmbeddings()

# 2. 加载CSV数据
loader = CSVLoader("data.csv", encoding="utf-8")
pages = loader.load_and_split()

# 3. 文本 → 向量
# 取出每个Document的文本内容
texts = [i.page_content for i in pages]
# embed_documents：输入多个文本, 输出多个向量（list of list）
embeded_docs = embeddings.embed_documents(texts)

print("向量数量:", len(embeded_docs)) # 向量个数 = 文本块数量
print("每个向量维度:", len(embeded_docs[0])) # 每个向量的维度（长度）
```

### 向量数据存储

从文档中加载数据，向量化后存储到数据库

```py
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# 加载文档
loader = CSVLoader("data.csv", encoding='utf-8')
pages = loader.load_and_split()

# 加载文档------>文本拆分
text_spliter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=500)
docs = text_spliter.split_documents(pages)

# 文本嵌入
embeddings = OpenAIEmbeddings()
# 向量存储存储
db_path = './chroma_db'
db = Chroma.from_documents(docs, embeddings, persist_directory=db_path)
```

### 向量检索

```py
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings

# 加载文档
loader = CSVLoader("data.csv", encoding='utf-8')
pages = loader.load_and_split()

# 文本拆分
text_spliter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=500)
docs = text_spliter.split_documents(pages)

# 向量化 + 存储
embeddings = OpenAIEmbeddings()
db_path = './chroma_db'
db = Chroma.from_documents(docs, embeddings, persist_directory=db_path)

# ========= 使用示例  ==========
# 1. 重新连接数据库, 重新加载已经存好的向量数据
db_new_connection = Chroma( 
    persist_directory=db_path,     # 指向之前保存的数据库目录
    embedding_function=embeddings  # 指向之前保存的数据库目录
)

# 2. 用户提问
question = '嘉柏湾的房子有那一些'
# 3. 相似度搜索
# question → embedding（转成向量）
# 和数据库里的向量做“相似度计算”
# 找最相似的前4个（默认top_k=4）
similar_docs = db_new_connection.similarity_search(question)

# 4. 查看结果
for doc in similar_docs:
    print(doc.page_content)

# ======== 使用 Retriever 检索（封装好的“检索器”）==========
retriever = db_new_connection.as_retriever()
sim_docs = retriever.invoke('嘉柏湾的房子有那一些')
for doc in sim_docs:
    print(doc.page_content)
```





## 使用示例

- **LangChain 使用示例**

  1. **定义系统提示词**：设定角色

     ```py
     SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.
     
     You have access to two tools:
     - get_weather_for_location: use this to get the weather for a specific location
     - get_user_location: use this to get the user's location
     
     If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location."""
     ```

  2. **创建工具**：定义工具函数，它们可以被 Agent 调用

     ```py
     from dataclasses import dataclass
     from langchain.tools import tool, ToolRuntime
     
     @tool # 把这个函数注册成 LLM 可以调用的 Tool
     # 获取城市天气
     def get_weather_for_location(city: str) -> str:
         """Get weather for a given city."""
         return f"It's always sunny in {city}!"
     
     @dataclass
     class Context: # 定义一个运行时上下文结构
         """Custom runtime context schema."""
         user_id: str # 存储用户信息
     
     @tool 
     # 根据用户ID(非普通参数,来自runtime) 获取位置
     def get_user_location(runtime: ToolRuntime[Context]) -> str:
         """Retrieve user information based on user ID."""
         # 从上下文里拿用户ID
         user_id = runtime.context.user_id 
         # 根据用户 ID 返回不同位置
         return "Florida" if user_id == "1" else "SF" 
     ```

     > 用户发起请求 → Agent 运行 → LLM 决定需要用户位置 
     >
     > → 调用 get_user_location() 
     >
     > → runtime 自动注入：runtime.context.user_id
     >
     > → Tool 返回位置
     >
     > → LLM 继续推理 / 调用其他工具

     > `ToolRuntime[Context]` 里面的 `[Context]` 是泛型，即 ToolRuntime 里面的 context 类型是 Context，Context 类型就是前面定义的 class Context

  3. **配置 Agent**：准备好 LLM 模型

     ```py
     from langchain.chat_models import init_chat_model
     
     model = init_chat_model(
         "claude-sonnet-4-6",   # 指定LLM模型
         temperature=0.5,       # 生成随机性（0更稳定，1更发散）
         timeout=10,            # 单次请求最大等待时间（秒），防止卡住
         max_tokens=1000        # 限制模型最大输出token数量（防止输出过长）
     )
     ```

  4. **定义响应格式（可选）**：告诉 LLM 必须按照这个格式输出，便于解析结果

     ```py
     from dataclasses import dataclass
     
     # We use a dataclass here, but Pydantic models are also supported.
     @dataclass
     class ResponseFormat:
         """Response schema for the agent.""" # 定义 LLM 输出的结构说明
         punny_response: str                  # 必填字段：一个带双关/幽默的回答
         weather_conditions: str | None = None  # 可选字段：天气信息（可为空）
     ```

     > `dataclass` 是 Python 的“轻量结构体”，是自动帮你生成“数据类模板”的语法糖。等价于：
     >
     > ```
     > class ResponseFormat:
     >     def __init__(self, punny_response, weather_conditions=None):
     >         self.punny_response = punny_response
     >         self.weather_conditions = weather_conditions
     > ```

  5. **添加记忆**：系统自动保存历史对话（上下文）→ 模型可以记住用户信息

     ```py
     from langgraph.checkpoint.memory import InMemorySaver  # 导入内存存储
     
     checkpointer = InMemorySaver()  # 创建一个“内存级”的状态存储器（程序关闭就没）
     ```

  6. **创建并运行 Agent**：

     ```py
     from langchain.agents.structured_output import ToolStrategy
     
     # 1. 创建Agent
     agent = create_agent( 	
         model=model, 		# 指定大模型（之前初始化的LLM）
         system_prompt=SYSTEM_PROMPT, # 系统提示词（控制Agent整体行为）
         tools=[get_user_location, get_weather_for_location],# 注册两个工具
         context_schema=Context, # 指定运行时上下文结构（定义了user_id等信息）
         response_format=ToolStrategy(ResponseFormat), # 指定输出格式
         checkpointer=checkpointer # 添加记忆
     )
     
     # thread_id 是一个会话唯一标识（用于区分不同用户/对话）
     config = {"configurable": {"thread_id": "1"}}
     
     # 2. 传入用户提问问题, 获取回答
     response = agent.invoke( # 调用agent的invoke方法, 包括执行一次LLM+Tool+Memory
         {"messages": [{"role": "user", "content": "what is the weather outside?"}]}, 
         config=config, # 传入线程ID（用于记忆）
         context=Context(user_id="1") # 注入运行时上下文（用户ID）
     )
     
     # 3. 打印回答结果
     print(response['structured_response']) 
     # ResponseFormat(
     #     punny_response="Florida is still having a 'sun-derful' day! The sunshine is playing 'ray-dio' hits all day long! ...",
     #     weather_conditions="It's always sunny in Florida!"
     # )
     
     # 4. 使用同一个 thread_id，可以继续对话，不会丢失上下文
     response = agent.invoke(
         {"messages": [{"role": "user", "content": "thank you!"}]},
         config=config,
         context=Context(user_id="1")
     )
     print(response['structured_response'])
     # ResponseFormat(
     #     punny_response="You're 'thund-erfully' welcome! It's always a 'breeze' to help you stay 'current' with the weather...",
     #     weather_conditions=None
     # )
     ```



