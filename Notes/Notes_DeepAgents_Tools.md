

## SDK、Tools、Skills

- **==SDK==（Software Development Kit，软件开发工具包）**

  - **本地依赖包**，在 Python 中就是一个通过 `pip install` 安装的库
  - **SDK 与 API 的关系**
    - **API**：远程服务器上的一个“地址”（例如：`https://api.tavily.com/search`）。如果你不用 SDK，你得自己写 `requests.post()` 去拼装 Header、处理状态码、解析 JSON。
    - **SDK** 把这些底层的 HTTP 网络请求封装成了 Python 函数。

- **==Tool==（工具）**：符合 Agent 框架接口协议的 “类” 或 “函数”。

  - 包含内容

    1. **Schema（描述信息）**：它用结构化的方式（通常是 JSON Schema）告诉 LLM：这个工具叫什么名、有什么用、需要什么参数。
    2. **执行动作**：当被调用时，具体运行哪段代码（通常内部就是调用了 SDK）。

  - **Tool 与 SDK 的关系**：<u>Tool 是 SDK 的“上层封装”</u>

    Tool 内部持有 SDK 的实例。Tool 把 SDK 的函数映射成了 LLM 能够理解的格式。
    
  - 在 Agent 开发中，<u>永远优先寻找“集成好的 Tool”</u>。
  
    如果你发现某个功能没有现成的集成 Tool，你才需要用你看到的 “原始 SDK” 写法，自己套一个 `@tool` 装饰器来把它包装成工具。
  
- **==Skills==（SKILL.md）**：是**自然语言描述**。它是给 Agent 看的“说明书”，告诉它“什么时候”该去用工具，以及用的“策略”是什么。



### 1. Tavily（联网搜索）

- **作用**：专用于 Agent 的搜索，它会搜索、抓取网页内容、清洗数据、做 Rerank（重排序）。

- **==环境配置==**

  - 安装依赖：`pip install deepagents langchain-community tavily-python python-dotenv`

  - 去 [Tavily 官网](https://tavily.com/) 申请一个免费的 API Key。

  - 在 `.env` 文件里写入：

    ```
    TAVILY_API_KEY=tvly-xxxxx
    ```

#### 手动包装 SDK 为 Tool

`from tavily import TavilyClient`

- **逻辑**：手动导入 `TavilyClient`，手动写函数，并手动把函数名放进 `tools` 列表。

- **优点**：灵活度高，你可以在函数里加自定义逻辑（比如过滤掉某网站）。

- **缺点**：工作量多，需要自己写函数名、参数类型、Docstring。

- **LLM 感知**：LLM 通过阅读你的 **Docstring** (即 `"""..."""`) 来理解工具。

- **使用示例**：

  ```py
  import os
  from tavily import TavilyClient
  from deepagents import create_deep_agent
  
  # 1. 实例化原始 SDK
  tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
  
  # 2. 手动将 SDK 函数包装成一个 Tool
  @Tool
  def search_tool(query: str):
      """当需要查询实时天气、新闻或最新资讯时使用此工具。"""
      # 手动调用 SDK 的 search 方法
      return tavily_client.search(query, max_results=3)
  
  # 3. 创建 Agent
  agent = create_deep_agent(
      model="openai:gpt-4o",
      tools=[search_tool],  # 传入你写的函数
      skills=["./skills/"]
  )
  ```

#### 直接使用已有 Tool

`from langchain_tavily import TavilySearch`

- **逻辑：** 不需要导入 `TavilyClient`，也不需要写 `def`。

  直接使用 `langchain_tavily` 已经为你写好的工具类。

- **优点**：只需一行代码

- **缺点**：灵活度低，只能修改它提供的参数（如 `max_results`）。

- **LLM 感知**：LLM 阅读工具类**内置的描述文本**来理解工具

- **示例**

  ```py
  import os
  from langchain_tavily import TavilySearch
  from deepagents import create_deep_agent
  
  # 1. 直接实例化现成的 Tool 对象 (它内部已经写好了 client.search 的调用逻辑)
  search_tool = TavilySearch(max_results=3)
  
  # 2. 创建 Agent
  agent = create_deep_agent(
      model="openai:gpt-4o",
      tools=[search_tool],  # 传入现成的对象
      skills=["./skills/"]
  )
  ```

  > ```py
  > # 将高级搜索改为基础搜索
  > search_tool = TavilySearchResults(max_results=2, search_depth="basic")
  > ```

- **已有 Tool 的内部行为**

  当你使用 `TavilySearchResults` 时，它内部其实就是一个高度标准化的 **“代码包装袋”**。它主要做了三件事：

  1. **自我介绍（Schema）**：它内置了一段说明：“我叫 `tavily_search_results_json`，我的作用是联网搜索信息，我需要一个参数叫 `query`。”
  2. **调用 SDK**：当你（Agent）决定要搜东西时，它在后台运行 `tavily_client.search(query)`。
  3. **翻译官**：它把搜索回来的那一堆乱七八糟的网页内容（HTML 或原始 JSON），精简成 LLM 最容易读懂的文本段落。

- **技术层级**

  1. **最底层 - API**：Tavily 的服务器
  2. **中间层 - SDK**：安装的 `tavily-python` 包，里面的 `TavilyClient` 类
  3. **应用层 - Tool**：`TavilySearchResults` 类。它在初始化时会自动创建一个 `TavilyClient`（或者接收你创建好的），并把自己包装成 Agent 能识别的工具。

- **架构设计**：

  Agent 的行为 = LLM 的常识 + Tool 的能力 + Skill 的约束

  **工具是“手”，而 Skill 是“大脑指令”。**

  虽然你的 Agent 手里拿着一把可以修任何东西的“万能扳手”（Tavily），但你在 `SKILL.md` 里下达了死命令：

  > “你现在的身份是天气与新闻助手。如果用户问你‘周杰伦的老婆是谁’，即使你能搜到，也要礼貌拒绝，并告诉他你只处理天气和新闻。”

  | **组件**              | **负责的事**                                     | **你的控制手段**           |
  | --------------------- | ------------------------------------------------ | -------------------------- |
  | **Tool（SDK包装）**   | **物理能力**：确保能连上网，拿回数据。           | 修改 `max_results` 等参数  |
  | **Skill（SKILL.md）** | **业务逻辑**：规定什么时候准搜，什么时候不准搜。 | 编写详细的规则和 SOP       |
  | **LLM**               | **判断力**：理解用户到底在问什么                 | 选择更聪明、更听指令的模型 |



### 2. 内容解析与抓取

Tavily 有时只能给你摘要，如果你想让 Agent 读完整个网页：

- **Jina Reader (r.jina.ai)**：**极其推荐！** 只要把 URL 传给它，它就能把整个网页转成干干净净的 Markdown 格式，非常适合喂给 LLM
- **Firecrawl**：把整个网站“爬”下来转成 AI 可读的数据



### 3. 数据处理与执行

- **Python Interpreter (Code Interpreter)**：给 Agent 一个沙盒环境跑 Python。它不仅能画图、做复杂数学运算，还能分析你上传的 Excel
- **Wolfram Alpha**：处理硬核数学、物理公式和专家级知识（比如：“对比土星和木星的质量”）



### 4. 自动化与生产力

- **Zapier / Make (Integramat)**：这是“万能插座”。接入一个 Zapier，你的 Agent 就能操作 5000+ 个应用（发邮件、写 Notion、发推特、查日历）。
- **Slack / Discord Webhooks**：让 Agent 查完资讯后，直接推送到你的工作群里。



### 5. 向量数据库（存储）

- **作用**：把文档存进向量数据库，让 Agent 用 RAG（检索增强生成）去查询。

#### 环境配置（ChromaDB）

- **==安装依赖==**：向量数据库核心库 +  OpenAI 的 Embedding（用于将文字转向量，最常用的模型）

  ```
  pip install chromadb langchain-openai langchain-community
  ```

- **==配置数据库并导入文件==**：创建一个 `ingest.py` 脚本，将你的本地文档（如 `data/` 目录下的文档）存入向量数据库。

  ```py
  import os
  from langchain_community.document_loaders import DirectoryLoader, TextLoader
  from langchain_openai import OpenAIEmbeddings
  from langchain_text_splitters import CharacterTextSplitter
  from langchain_community.vectorstores import Chroma
  
  # 1. 加载文档
  loader = DirectoryLoader('./data/', glob="./*.txt",
                           loader_cls=TextLoader)
  documents = loader.load()
  
  # 2. 切分文档
  text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
  docs = text_splitter.split_documents(documents)
  
  # 3. 创建向量库并持久化到本地目录 ./chroma_db
  vectorstore = Chroma.from_documents(
      documents=docs,
      embedding=OpenAIEmbeddings(), # 需要环境变量中有 OPENAI_API_KEY
      persist_directory="./chroma_db"
  )
  print("数据库创建成功！")
  ```

- **向量数据库**：= 一个 “拥有超级索引功能“ 的本地文件夹。只要备份好那个目录，你的 Agent 的 “知识” 就永远不会丢失。

  - **嵌入式**：ChromaDB 不需要像 MySQL 或 SQL Server 那样先安装软件。它默认是“嵌入式数据库”。只要 `pip install chromadb`，它就在你的代码库里了。

  - **创建向量数据库**：创建过程完全由代码触发。

    当执行 `persist_directory="./chroma_db"` 时，代码运行的当前文件夹下会多出一个叫 `chroma_db` 的文件夹。

  - **存储逻辑**：它把你的文档转换成数字，然后利用像 `HNSW` 这样的算法进行排序。这些排序后的结果被直接写进你指定的那个本地目录。

  - **本地可见性**：你可以随时打开那个目录。你会看到一些 `.sqlite3` 文件（它底层其实就是用了 SQLite 来存元数据）和一些存向量的索引文件。

  - **为什么向量库这么轻量？** 因为目前的 RAG 应用大多是“个人”或“单机”性质的。你不需要像银行系统那样每秒处理几万笔转账，你只需要 Agent 能快速翻阅你硬盘上的几本书。

#### 在 DeepAgents 中使用

- **先==初始化这个数据库==**：

  ```py
  from langchain_community.vectorstores import Chroma
  from langchain_openai import OpenAIEmbeddings
  
  # 加载已经存在的数据库
  db = Chroma(persist_directory="./chroma_db",
              embedding_function=OpenAIEmbeddings())
  ```

- **方式1：==手动封装为 Tools==**（推荐）

  > **调试方便**：你可以在函数里加 `print(results)`，实时看到 Agent 到底从库里翻出了什么。
  >
  > **后处理逻辑**：你可以在返回给 Agent 之前，自己对结果做清洗、排序或格式化（例如加上“以上内容来自公司内网”）。
  >
  > **完全掌控**：DeepAgents 的精髓就在于 `Tool` 只是一个普通的 Python 函数，手动封装能让你像写普通业务逻辑一样控制 RAG。

  ```py
  def query_knowledge_base(query: str):
      """
      当用户问到关于公司内部政策、私有技术文档或特定背景资料时，必须使用此工具查询。
      """
      # 搜索最相关的 3 条内容
      results = db.similarity_search(query, k=3)
      return "\n\n".join([res.page_content for res in results])
  
  # 传给 DeepAgents
  agent = create_deep_agent(
      model="deepseek:deepseek-chat",
      tools=[query_knowledge_base], # 放入自定义Tools
      system_prompt="你是一个资讯专家，请优先查阅本地知识库回答问题。"
  )
  ```

- **方式2：使用已有 Tool**（不建议）

  > `retriever_tool` 是 LangChain 为了偷懒设计的**“高阶封装对象”**。它不仅仅是一个函数，而是一个包含了 `name`、`description` 和 `args_schema` 的 **对象**。
  >
  > 即使使用了它，你依然要先实例化数据库（DB）、配置检索器（Retriever）。
  >
  > 而且它把 “检索逻辑” 锁死在 LangChain 内部。如果 Agent 检索出来的东西不对，你很难在中间插手去调试。

  ```py
  from langchain.tools.retriever import create_retriever_tool
  
  # 直接把数据库变成一个 Retriever Tool
  retriever_tool = create_retriever_tool(
      db.as_retriever(),
      name="internal_knowledge_search",
      description="用于检索本地存储的所有专业文档和私有资料。"
  )
  
  # 传给 DeepAgents
  agent = create_deep_agent(
      model="deepseek:deepseek-chat",
      tools=[retriever_tool], # 这里直接放 LangChain 生成的工具对象
      system_prompt="你是一个资讯专家..."
  )
  ```

  



## Demo

- ???

  - **环境**： `pip install deepagents langchain_openai`

  - **示例**

    ```py
    from deepagents import create_deep_agent
    from langchain_core.tools import tool #用于把一个普通函数“注册”为工具（给 agent用）
    
    # 1. 定义天气工具
    @tool # 使用 @tool 装饰器，把这个函数注册为一个工具
    def get_weather(city: str) -> str:
        """获取指定城市的实时天气。"""
        # 实际开发中这里会接入 OpenWeather API
        return f"{city}今天晴转多云，25°C。"
    
    # 2. 定义新闻工具
    @tool
    def search_news(topic: str) -> str:
        """搜索关于某个话题的最新新闻。"""
        # 实际开发中这里会接入 Tavily 或 DuckDuckGo
        return f"关于 {topic} 的最新头条：AI Agent 框架 DeepAgents 正式发布！"
    
    # 3. 创建 Deep Agent (核心区别在于这个方法)
    # 它会自动为你构建 Planning（规划）和 Reflection（反思）节点
    agent = create_deep_agent(
        model="openai:gpt-4o",  # 或 "claude-3-5-sonnet"
        tools=[get_weather, search_news],
        system_prompt="你是一个高效的个人助理，负责通过工具获取信息并总结。"
    )
    
    # 4. 运行并查看逻辑
    response = agent.invoke({
        "messages": [{"role": "user", "content": "帮我查一下上海的天气，并搜一下今天关于 DeepAgents 的新闻。"}]
    })
    
    print(response["messages"][-1].content)
    ```

  - 这个 Agent 到底是怎么 run 起来的？——**DeepAgents 的“执行图 (Execution Graph)”**。

    与普通 LangChain Agent 不同，DeepAgents 的内部是一个由 **LangGraph** 驱动的状态机。你可以尝试在代码里加上这一行来观察它的结构：

    ```py
    # 打印执行图的节点，看看它比起普通 Agent 多了哪些步骤
    print(agent.get_graph().nodes.keys())
    ```

    你会发现它不仅仅有 `call_model` 和 `call_tools`，通常还包含：

    1. **Planning (规划层)**：它接收到用户指令后，会先生成一个“任务清单”（Todo List），决定先查天气还是先搜新闻。
    2. **State Management (状态层)**：它会把天气结果存入“短期记忆”，供搜索新闻时参考（例如：如果天气不好，它可能会在搜新闻时自动增加“暴雨预警”的搜索项）。
    3. **Reflection (反思层)**：在给用户最终答案前，它会自我检查：“我查到的天气和新闻完整吗？有没有遗漏？”

  - 建议你在跑通代码后，重点研究以下三点：

    1. **观察日志 (Tracing)**：使用 **LangSmith**（LangChain 的可视化工具）观察。你会看到 DeepAgents 在后台会进行多次 LLM 调用，甚至会有自己跟自己对话（规划步骤）的过程。
    2. **研究“中介软件 (Middleware)”**：DeepAgents 的一大特色是支持 Middleware。你可以尝试写一个简单的 Middleware，在工具被调用前打印一条 Log，这样你就理解了它在执行流程中是如何拦截信息的。
    3. **对比实验**：你可以尝试用普通的 `create_react_agent` (LangChain 原生) 和 `create_deep_agent` 处理同一个复杂问题。你会发现 DeepAgents 在处理“先做什么、后做什么”的逻辑上要聪明得多。

- 

