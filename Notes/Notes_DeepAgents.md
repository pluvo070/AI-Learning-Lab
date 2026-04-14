# DeepAgents

## 环境配置

### 资源准备

- **官方资源**

  - **官方文档：** https://docs.langchain.com/oss/python/deepagents/quickstart
  - **GitHub 仓库：** [github.com/langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) (内含大量的 `examples` 文件夹)
  - **NPM / PyPI：** 搜索 `deepagents` 查看最新的包版本和简易 README

- **环境管理**

  - **Anaconda**：https://www.anaconda.com/（左侧下载）

    > Conda 是一个**环境管理器**和**包管理器**。你在环境 A 里乱装东西弄坏了，只需要把这个环境删了就行，不会影响你电脑本身的系统或其他项目的运行。

  - **Miniconda**：https://www.anaconda.com/（右侧下载）

    > 轻量级 conda，它只包含 `conda`、`python` 和一些基础工具，下载和安装都非常迅速。说明文档： [Miniconda - Anaconda](https://www.anaconda.com/docs/getting-started/miniconda/main)

### 配置步骤

- **打开 conda**：运行程序 Anaconda Prompt 

- **同意条款**：首次创建环境前需要手动同意 Anaconda 的服务条款

  ```bash
  conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
  conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
  conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
  ```

- **创建环境并进入**

  ```bash
  conda create -n py312-deepagents-202604 python=3.12 -y # 创建环境
  conda env list # 查看所有环境列表
  conda activate py312-deepagents-202604 # 切换到环境
  ```

- **进入项目目录，安装依赖**

  ```bash
  cd /d D:\Code\LLM\Exercises\weather_news_agent # 切换到D盘的工作目录
  pip list # 查看所有依赖
  pip install deepagents langchain-deepseek python-dotenv # 安装所需依赖
  pip list --format=freeze > requirements.txt # 导出依赖列表
  ```

  > 配置国内镜像源：如果 `pip install` 太慢，可以在命令行先换成清华源
  >
  > ```
  > pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
  > ```

- **启动 IDE**：

  - **命令行启动**：如果你安装了 Cursor 的命令行工具，你可以输入 `cursor .`
  
  - **选择环境【重要】**： 打开 Cursor 后，你必须告诉它使用你刚创建的 Conda 环境，否则代码会报错（找不到 `deepagents`）。
    
    - 快捷键：`Ctrl + Shift + P`
    - 输入：`Python: Select Interpreter`
    - 在列表中找到：`Python 3.12 ('py312-deepagents-202604': conda)`
    
    > 每次打开 IDE 都需要确认环境，但是不需要每次打开 IDE 都再开 Anaconda CLI。
    >
    > 什么时候需要再次手动 `conda activate`：
    >
    > - 在终端里手动跑 Python / pip / 脚本：`python xxx.py`
    > - 用命令行执行：`pip install xxx`
  
  

## 使用模型

- **模型运行方式**

  - **远程模式（API）**

    - 当你运行 `agent.invoke` 时，你的电脑会通过网络把你的问题（比如“查天气”）打包发给 DeepSeek 的机房。计算位置在DeepSeek 昂贵的显卡（GPU）阵列上。你的电脑只负责**发送请求**和**接收文字**。

    - **DEEPSEEK_API_KEY**：https://platform.deepseek.com/

      > 如何选用模型：在代码中填写 `model` 参数时指定
      >
      > `deepseek-chat`：入门推荐，响应快，对应的是最新的 DeepSeek-V3.2，适合日常对话、总结、写代码。
      >
      > **`deepseek-reasoner`**：对应的是带“思维链”的模型（类似 OpenAI 的 o1），用于解决复杂数学题或逻辑陷阱。

  - **本地模式（Local LLM）**
    - 如果想在自己电脑上跑，需要使用 **Ollama** 这种工具下载模型文件（几 GB 到几十 GB），那时计算才会在你的 CPU/GPU 上运行。

### 远程模型

- **配置环境变量**：在项目根目录创建一个 `.env` 文件，放入你的 API Key

  ```
  DEEPSEEK_API_KEY=...
  OPENAI_API_KEY=...
  ```

  > sk-309722f8dd5d4c3cb78a91bd5c01af53

- **使用示例**：初始化一个具备深度思考能力的 Agent，并实现一个简单的交互式命令行对话

  ```py
  from deepagents import create_deep_agent # 用于创建Agent
  from dotenv import load_dotenv # 用于加载环境变量
  load_dotenv() # 加载环境变量(API KEY)
  
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
      # 遍历模型返回的所有消息
      # results["messages"] 是一个列表，里面包含对话内容（用户 + AI）
      for message in results["messages"]:
          message.pretty_print() # 格式化打印消息
  ```

- **运行程序**：在 Anaconda Prompt 窗口 `python 脚本.py`

  > <img src="pictures/DeepAgents-01.png" alt="DeepAgents-01" style="zoom:38%;" />

- `agent.invoke()` 返回的是什么：

  一个字典（dict），里面包含完整的对话结果，`print(results)` 可以看到其结构。

  > ```
  > results = {
  >     "messages": [
  >         HumanMessage(...),      # 用户消息
  >         AIMessage(...)        	# AI 回复
  >     ]
  > }
  > ```
  >
  > `results` 是一个 **字典**（键值对 ≈  `Map<String, List<Message>>`），其中 `:` 用于分隔一对键值对中的键和值，若有多个键值对则用 `,` 分隔。
  >
  > `"messages"` 是键（字符串）
  >
  > `[...]` 是值，这个值是一个 **列表**（List ≈ `ArrayList`）
  >
  > 这个列表里有两个元素，一个是 `HumanMessage` 对象，一个是 `AIMessage` 对象

### 本地 Ollama 

- **前置条件**：

  - 安装 Ollama

  - 下载大模型

    > ```bash
    > # 查看有哪些模型
    > (py312-deepagents-202604) D:PATH> ollama alist
    > ```

  - 安装依赖：`pip install langchain-ollama`

- **代码示例**：在远程代码的基础上，只需要更改使用的模型这一行即可

  ```py
  # 创建一个Agent, 指定模型
  agent = create_deep_agent(
      model="ollama:qwen3:8b" 
  )
  ```



## Agent 基础配置

### 创建 Agent `create_deep_agent` 

```py
create_deep_agent(
    name=None,              # agent名字 (可选)
    model=None,             # 模型名 (可选, 默认claude-sonnet-4-6)
    tools=None,             # 工具列表 (可选)
    system_prompt=None,     # 系统提示 (可选)
    middleware=None,		# 中间件 (可选)
    subagents=None,			# 子代理 (可选)
    backend=None,			# 后端 (可选, 默认StateBackend)
    store=None				# 物理存储位置(可选, 存储型后端才需要)
) -> CompiledStateGraph    	# 返回一个 Agent 对象
```

| **阶段**             | **参数/概念**                 | **解决的问题**                             | **现实比喻**                                                 |
| -------------------- | ----------------------------- | ------------------------------------------ | ------------------------------------------------------------ |
| **基础配置**         | `model`, `tools`              | Agent 拿什么思考和工作？                   | 员工的智力和工具                                             |
| **工作流程**         | **Graph**, **GraphState**     | Agent 工作的步骤是什么？中间数据长什么样？ | 公司的**标准作业程序 (SOP)** 和当前的**工作表单**            |
|                      | **Middleware**, **Subagents** | /                                          | **Middleware**: 规章制度（进出都要查）。**Subagents**: 下属部门或外包团队。 |
| **持久化 (Backend)** | **Checkpointer** & **State**  | 对话中断了，重启后怎么接上？               | 秘书给工作表单**拍的照片（存档）**                           |
| **持久化 (Backend)** | **Store**                     | 任务结束了，学到的经验存哪？               | 公司的**长期档案室**                                         |



### 模型 `model` 

```py
agent = create_deep_agent(
    model=init_chat_model(
        model="claude-sonnet-4-6",
        max_retries=10,  # 重试失败的 API 请求 (default: 6)
        timeout=120,     # Increase timeout for slow connections
    ),
)
```

> 使用 openai 模型需要先：`pip install langchain-openai`

### 工具 `tools` 

> https://github.com/langchain-ai/deepagents/tree/main/examples

- **==自定义工具函数==**：`from langchain_core.tools import tool` + `@tool`

  ```py
  from deepagents import create_deep_agent
  from langchain_core.tools import tool #用于把一个普通函数“注册”为工具（给 agent用）
  
  # 1. 定义工具函数
  @tool  # 使用 @tool 装饰器，把这个函数注册为一个工具
  def get_weather(city: str) -> str:
      """Get weather for a given city."""
      return f"It's always sunny in {city}!"
  
  # 2. 配置和创建agent
  agent = create_deep_agent(
      model="openai:gpt-5.4", 						# 指定模型
      tools=[get_weather],							# 绑定工具
      system_prompt="You are a helpful assistant", 	# 系统prompt
  )
  
  # 3. 运行agent
  agent.invoke(
      {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
  )
  ```

  > 示例 2 见：LLM\deepagents-202604\03-tools.py

### 系统提示 `system_prompt` 

- 系统提示是启动 Agent 时最顶层的指令（通常由框架自动生成或用户注入）。
  - <u>用于定义 AI 的角色身份</u>，例如 “你是一个冷酷的机器人” 或 “你是一个热情的导游”。
  - 它太宏观了。如果你在 System Prompt 里写太细的工具使用逻辑，模型容易遗忘。
- Agent 有一个默认系统提示，其中包含使用内置规划工具、文件系统工具和子代理的详细说明。当中间件添加特殊工具，比如文件系统工具时，会将其附加到系统提示符中。

```py
research_instructions = """\
You are an expert researcher. Your job is to conduct \
thorough research, and then write a polished report. \
"""

agent = create_deep_agent(
    system_prompt=research_instructions,
)
```





## Agent 的运行流程

### 图与图状态

#### GraphState（图状态）

- **定义**：一个 <u>数据结构</u>，是一个普通的 Python 类（通常用 `TypedDict` 或 `Pydantic` 定义），它规定了 Agent 在思考过程中，**脑袋里能记住哪些信息**。

- **为什么需要它**：AI 模型本身是 “无记忆” 的。为了让它能进行多步推理，我们需要一个容器来装中间结果。

  GraphState 就像一张**随身携带的表格**。Agent 每走一步，都会查这张表，并在表上写新东西。

#### Graph（图）

- **定义**：<u>控制流</u>，定义 Agent 思考的步骤。比如：`接收问题 -> 思考 -> 调工具 -> 观察结果 -> 回答`。

- **结构**：

  - **==Node==（节点）**：<u>执行单元</u>。本质上就是一个 Python 函数。它接收当前的 `State`，做点事情，然后返回更新后的 `State`。

    > **节点 1 (思考)**：把问题发给大模型
    >
    > **节点 2 (执行)**：去查数据库
    >
    > **节点 3 (反思)**：检查结果对不对

  - **==Edge==（边）**：动作顺序，<u>决策逻辑</u>，决定节点之间怎么跳。
    - **普通边**：节点 A 结束后，永远跳到节点 B。
    - **条件边（Conditional Edges）**：根据状态判断。如果 AI 说 “我要查天气”，就跳到 “工具节点”；如果 AI 说 “我写好了”，就跳到 “结束”。

#### 定义图并编译为 Agent

1. **定义一个图状态（State 结构）**：

   ```py
   from typing import Annotated, TypedDict
   from langgraph.graph.message import add_messages
   
   # 定义 State 结构
   class MyAgentState(TypedDict):
       # 定义messages变量，它的值是一个列表，且新数据会自动追加
       messages: Annotated[list, add_messages] 
       # 可以自定义任何变量，比如对话次数
       count: int
   ```

   > - `class MyAgentState(TypedDict):`：表示 MyAgentState 继承了 TypedDict
   >
   > - `messages: Annotated[list, add_messages]`：定义了一个键值对
   >
   >   键是字符串 `messages`；值是 `list` 类型的，且有注解 `add_messages`。

2. **定义图的节点**：`state` 这个参数是框架在运行时传进去的

   ```py
   # 初始化模型
   llm = ChatOpenAI(model="gpt-4o")
   
   # 节点 1: 调用 LLM 的节点
   def node_agent(state: MyAgentState):
       # 拿来全部的历史消息
       input_messages = state["messages"]
       # 把消息喂给 LLM，让它思考并回答，llm.invoke() 会返回一个消息对象
       response = llm.invoke(input_messages)
       # 把LLM的回答包装成字典返回，框架会自动将其中的response加入messages列表
       return {"messages": [response]}
   
   # 节点 2: 纯 Python 逻辑的节点，这个节点不求助于 LLM，而是由程序自己判断
   def node_count(state: MyAgentState):
       return {"count": state["count"] + 1} # 更新对话次数
   ```

3. **把节点组装成图（流水线）**：

   ```py
   from langgraph.graph import StateGraph, START, END
   
   # 1. 声明：我要建一个流水线，它处理的数据格式是 MyAgentState
   workflow = StateGraph(MyAgentState)
   
   # 2. 注册：把刚才写的节点组装进流水线
   workflow.add_node("agent_node", node_agent)
   workflow.add_node("counter_node", node_count)
   
   # 3. 连线：规定执行顺序
   workflow.add_edge(START, "agent_node")       	# 起点 -> LLM节点
   workflow.add_edge("agent_node", "counter_node") # LLM节点 -> 计数节点
   workflow.add_edge("counter_node", END)       	# 计数节点 -> 终点
   ```

4. **把图编译为一个可执行的 Agent**：

   ```py
   app = workflow.compile()
   ```

5. **运行 Agent**：当调用 `invoke` 时，`state` 变量才真正诞生

   ```py
   # 你传进去的这个字典，就是 state 的“初始状态”
   initial_input = {
       "messages": [("user", "你好，请简单介绍一下你自己")], 
       "count": 0
   }
   # 框架拿到它后，会把它包装成 MyAgentState 格式，开始在节点间传递
   final_state = app.invoke(initial_input)
   
   print(f"最终对话次数: {final_state['count']}")
   print(f"最后一条 AI 回复: {final_state['messages'][-1].content}")
   ```

#### 运行流程

1. **触发与初始化**

   1. **用户动作**：用户输入 “你好，我是张三”。
   2. **前端调用**：程序调用 `app.invoke({"messages": [...]}, config={"thread_id": "1"})`。
   3. **恢复现场（如果有 Backend）**：
      - 框架看到 `thread_id: 1`。
      - **Backend** 介入：去数据库查一下，这个 ID 之前有进度吗？
      - **结果**：如果是新对话，创建一个空的 `state` 变量（ `MyAgentState` 类型）；如果是旧对话，从数据库捞出旧的 `state` 覆盖它。

2. **进入图流转（The Graph Flow）**

   1. **起点**：快递员（框架引擎）带着 `state` 跑向第一个节点 `agent_node`。

   2. **节点处理**：

      - `node_agent(state)` 函数被激活，函数内部执行 `response = llm.invoke(state['messages'])`。
      - **LLM 思考**：LLM 收到历史消息，算出一串 Token：“你好张三，我记住了。”
      - **返回更新**：函数返回 `{"messages": [response]}`。

   3. **状态合并 (State Merging)**：

      框架收到返回的字典，由于 `messages` 定义了 `add_messages`，框架**不会替换**原来的消息，而是把 AI 的话**追加**到列表末尾。

3. **节点切换**

   1. **边逻辑**：框架查看连线，发现下一步要去 `counter_node`。
   2. **逻辑处理**：
      - `node_counter` 被激活。它直接把 `state['retry_count']` 加 1。
      - 返回 `{"retry_count": 1}`，框架更新 `state`。

4. **执行终点**

   1. **图运行结束**
   2. **自动持久化（Backend）**：
      - 一旦到达 `END`，框架会自动触发 **Checkpointer/Store**。
      - **动作**：将最终那个包含“用户：你好”、“AI：你好张三”以及 `count: 1` 的完整 `state` 对象，打包序列化。
      - **存入**：写入 Postgres 数据库的 `checkpoints` 表。
   3. **返回结果**：把这个最终状态返回给用户界面。

----

| **阶段**     | **state["messages"] 内容**             | **state["count"]** | **操作者**      |
| ------------ | -------------------------------------- | ------------------ | --------------- |
| 1. 初始输入  | `[User: 你好，我是张三]`               | `0`                | 用户/开发者     |
| 2. 节点1内部 | `[User: 你好，我是张三]`               | `0`                | 调用 LLM 前     |
| 3. 节点1结束 | `[User: 你好，我是张三, AI: 你好张三]` | `0`                | 框架自动合并    |
| 4. 节点2结束 | `[User: 你好，我是张三, AI: 你好张三]` | `1`                | 框架自动合并    |
| 5. 持久化后  | `[User: 你好，我是张三, AI: 你好张三]` | `1`                | Backend 存入 DB |

### create_deep_agent 的图

- **==create_deep_agent 本质==**：一个 “<u>Agent 工厂</u>”

  它预先设计好了一套工业级的、通用的图结构。你只需要把“零部件”（模型、工具、后端）传进去，它就自动帮你组装好。

- **==create_deep_agent 内部的图==**：<u>ReAct</u>（Reasoning and Acting）架构，图的 “形状” 是写死的，但 “开关” 是动态的，循环往复直到满意。

  - ***Call Model*（决策节点）**： LLM 所在
    
    - **动作**：拿着 `state["messages"]` 去问 LLM：“下一步干什么？”
    - **逻辑**：如果 LLM 回复文本，就去“结束”；如果 LLM 返回 `tool_calls`（想调工具），就去下一个节点。
    
  - ***Tool Execution*（执行节点）**：Tools 所在
    
    - **动作**：自动根据 LLM 的要求，运行你传入的 `tools` 列表里的函数。
    - **逻辑**：把函数运行的结果（比如天气数据）包成一条 `ToolMessage` 存入 `state`。
    
  - ***边（Edges）***：Router

    1. 从 `START` 到 `Agent Node` （固定）
    2. **条件边**：从 `Agent Node` 出发，根据 LLM 的输出做判断：
       - 如果 LLM 说 “我要调工具”，走 A 路径去 `Tools Node`。
       - 如果 LLM 说 “我回答完了”，走 B 路径去 `END`。
    3. 从 `Tools Node` 回到 `Agent Node`（固定，形成循环）

    > `create_deep_agent` 内部写死了一个**循环结构**。它能够处理动态需求，不是因为它改变了图的形状，而是因为它在边上加了“逻辑闸门”。
    >
    > - **如果用户问“你好”：** 数据流路径是 `START` -> `Agent` -> `END`。
    > - **如果用户问“查天气”：** 数据流路径是 `START` -> `Agent` -> `Tools` -> `Agent` -> `END`。

    > 条件边的伪代码实现：
    >
    > ```py
    > # 这是一个决策函数，决定下一步去哪
    > def should_continue(state: MyAgentState):
    >     messages = state['messages']
    >     last_message = messages[-1]
    >     # 动态判断：最后一条消息是否有工具调用请求？
    >     if last_message.tool_calls:
    >         return "tools"  # 告诉框架：下一站去工具节点
    >     return END          # 告诉框架：下一站去结束
    > 
    > # 在构建图时，它是这样“写死”的：
    > workflow.add_conditional_edges(
    >     "agent_node",      # 从这个节点出发
    >     should_continue    # 使用这个函数来做动态判断
    > )
    > ```

- **==state 生命周期==**

  假设你用 `create_deep_agent` 问：“今天上海天气如何？”（你提供了一个 `get_weather` 工具）。

  | **步骤** | **节点**       | **State 内容变化**                                        |
  | -------- | -------------- | --------------------------------------------------------- |
  | **1**    | **START**      | `[User: 上海天气？]`                                      |
  | **2**    | **Call Model** | `[User: 上海天气？, AI: (我要调 get_weather, 城市=上海)]` |
  | **3**    | **Tools**      | `[..., AI: (调工具), Tool: (上海 20度)]`                  |
  | **4**    | **Call Model** | `[..., Tool: (上海 20度), AI: 上海今天 20 度。]`          |
  | **5**    | **END**        | 最终 State 被传给 Backend 存入数据库                      |

- **什么时候需要从 0 开始写图，而不用 create_deep_agent ？**

  - **强流程控制**：比如你要求 Agent 必须先查 A，再查 B，最后必须让一个“人工审核节点”通过才能回复。
  - **多智能体协作**：你需要一个主 Agent 分发任务给三个子 Agent。
  - **复杂自省**：你需要 Agent 在回答后，自己跳到一个“反思节点”检查自己的错误，如果错了就打回去重写。



## 中间件与子代理

### 中间件 `middleware` 

- **工具和中间件的区别**

  - 工具 = 让模型 “做事情” 的能力
  - 中间件 = 控制 / 增强工具调用过程；管流程（不做事，只管怎么做）

- **执行位置**：**Graph（图）** 的节点执行前后（在 `create_deep_agent` 执行具体任务之前或之后拦截数据。）

  它不是 Agent 的“脑细胞”，而是包在脑细胞外面的“保护膜”。

- **作用**：打印日志、权限控制、限流、参数过滤、安全审计

  - **输入加工**：在 Agent 看到用户话之前，先把敏感词滤掉，或者翻译成英文。
  - **输出拦截**：在 Agent 回答之后，检查格式是否正确（比如是否是合法的 JSON）。
  - **日志记录**：偷偷把 Agent 的思考过程存到你指定的后台。

  > 下例中 `log_tool_calls` 函数的作用是：拦截工具调用，在调用前/后插入打印日志的逻辑，不改变工具本身。

#### wrap_tool_call 型中间件

- `wrap_tool_call`：专门用于 “拦截 tool 调用” 的中间件注册器

  执行流程：`Agent → middleware → tool → middleware → Agent`

  > 还有用于拦截 agent 输入输出、拦截 LLM 请求等的不同类型中间件，需要导入不同包，使用不同装饰器注册。

- **参数 `request` 和 `handler`**：是框架定义的固定协议，就像是插头和插座的关系。

  - `@wrap_tool_call` 这个装饰器在后台工作时，它期望接收到的函数必须满足双参数签名：第一个参数接收当前的请求上下文。第二个参数接收执行逻辑的下一步函数。

  - **`request` (快递单)**：一个对象，包含了 AI 想要干什么的所有信息。

    它里面有：`request.name`（工具的名字，比如 "get_weather"）和 `request.args`（参数，比如 `{"city": "Shanghai"}`）。

  - **`handler` (快递员)**：一个可执行的函数。

    它的作用是把“快递”送往下一站。如果你不调用 `handler(request)`，这个工具调用就会被“拦截”在中间件里，永远不会执行。

- **调用流程**：你永远不需要手动调用 `log_tool_calls`。 实际的传参是由 Agent 内部的执行引擎自动完成的。

  1. **AI 发出指令**：模型说“我想调用 `get_weather`，参数是 `Shanghai`”。
  2. **框架封装 Request**：框架生成一个对象：`ToolRequest(name="get_weather", args={"city": "Shanghai"})`。
  3. **框架触发中间件**：
     - 框架自动把这个对象传给 `request`。
     - 框架把真正的工具函数（即 `get_weather`）包装成一个函数，传给 `handler`。
  4. **执行工具函数**：执行 `result = handler(request)` 时，程序才真正进入到工具函数 `@tool get_weather` 里。

```py
from langchain.tools import tool # 用于注册工具函数
from langchain.agents.middleware import wrap_tool_call # 用于定义拦截tool调用型的“中间件”
from deepagents import create_deep_agent # # 用于创建一个agent

# 1. 定义工具函数
@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

# 创建一个列表，用来记录调用次数
call_count = [0]  

# 2. 定义一个中间件, 使用@wrap_tool_call注册, 这个函数会在“每次工具调用前后”被执行
# request：工具调用请求（包含工具名、参数等）
# handler：真正执行工具的函数（必须调用它）
@wrap_tool_call
def log_tool_calls(request, handler):
    """Intercept and log every tool call - demonstrates cross-cutting concern."""
    call_count[0] += 1 # 每次调用工具时，计数 +1
    # 获取工具名称（如果有 name 属性）
    tool_name = request.name if hasattr(request, 'name') else str(request)
	# 打印日志：第几次调用 + 工具名称
    print(f"[Middleware] Tool call #{call_count[0]}: {tool_name}")
    # 打印工具参数（如果有 args 属性）
    print(f"[Middleware] Arguments: {request.args if hasattr(request, 'args') else 'N/A'}")
    # 调用 handler 才会真正执行工具，即调用 get_weather
    result = handler(request)
    # 打印调用完成日志
    print(f"[Middleware] Tool call #{call_count[0]} completed")
	# 返回工具执行结果（必须返回）
    return result

# 3. 创建一个 agent
agent = create_deep_agent(
    tools=[get_weather], # 注册工具（模型可以调用这些函数）
    middleware=[log_tool_calls], # 注册中间件（会包裹工具调用过程）
)
```

#### 中间件设计原则

**把中间件当成“无状态”的函数**

- 成员变量 `self.x` 只用来放那些<u>永远不会变</u>的配置（比如 API Key 或超时时间）

  > 在普通的 Python 编程中，我们习惯用 `self.x = 1` 来记录某个数值。但在这种 AI 代理（Agent）框架中，中间件（Middleware）通常是**单例**或**共享**的。
  >
  > **错误做法：** 你在 `__init__` 里定义了 `self.x`，然后在 `before_agent` 里修改它。
  >
  > **后果：** 想象一下，如果有 10 个用户同时在调用这个 AI，或者 AI 正在并行运行 5个工具。这所有的线程都会**同时**去修改同一个 `self.x`。
  >
  > **竞态条件（Race Condition）：** 线程 A刚读取 `x=1` 准备加 1，线程 B 已经把 `x` 改成了 2。结果线程 A 写回时还是 2，而不是预期的 3。这就会导致计数不准或程序崩溃。

- **使用 ==“图状态”（Graph State）==**：任何需要<u>累加、计数、记录</u>的数据，全部通过 `state.get()` 读取并随 `return` 更新。

  - **Graph**：LangGraph 定义的 AI 任务的流程图

    - **节点（Nodes）：** 是具体的动作（比如调用模型、搜索网页）
    - **边（Edges）：** 是动作之间的连线
    
  - **Graph State**：线程安全的全局上下文，图状态和 `self.x` 的本质差异在于它的作用域（Scope）。
  
    每当流程走到一个节点时，框架会把这个“快递盒”交给你。你可以查看盒子里有什么，也可以往里加东西，然后传给下一个节点。
    
    - **数据结构**：一个 Python 字典 (TypedDict) 或 Pydantic 模型
    - **生命周期：** 随着 “一次对话请求” 的产生而产生，随着请求结束而销毁
    - **并发设计：** DeepAgent 会确保每个独立的用户请求都有一个完全隔离的字典副本。即使 100 个人同时提问，框架也会准备 100 个“快递盒”，互不干扰
  
- **使用示例**：使用图状态分为三个步骤：定义、读写、合并。

  - 定义 Schema（告诉框架盒子里装什么）

    ```py
    from typing import TypedDict
    
    class MyGraphState(TypedDict):
        counter: int
        user_input: str
        history: list
    ```

  - 在中间件或节点中读写：当编写 `before_agent` 时，框架会自动把当前的 `state` 传给你。

    ```py
    def before_agent(self, state: MyGraphState, runtime):
        # 1. 读取（Read）
        current_count = state.get("counter", 0)
        
        # 2. 返回更新（Update）
        # 注意：不要原地修改 state['counter'] = x
        # 而是返回一个包含更新内容的字典，框架会自动帮你“合并”
        return {"counter": current_count + 1}
    ```

  - 自动合并（Reducer）：大多数框架支持 **Reducer** 模式：

    - 如果返回的是 `{"counter": 2}`，它会**覆盖**旧的值。
    - 如果你定义了特定的合并方式（比如列表），返回 `{"history": ["新消息"]}` 时，它会自动**追加**到旧列表后面，而不是替换掉。

### 子代理 `subagents`

**Subagents** 是在 **Tools（工具）** 层级之上的逻辑组件。

- **在结构中的位置**：它们通常被当作 **“超级工具”**。在你的 `create_deep_agent` 参数列表里，你可以把一个 Subagent 包装成一个 Tool 传给主 Agent。

- **它做什么**：隔离详细工作、避免上下文膨胀

  - 主 Agent 发现任务太难（比如：写一个 5000 字的研报并画图）。
  - 主 Agent 不亲自写，而是调用一个专门写报告的 **Subagent A** 和一个专门画图的 **Subagent B**。

  **逻辑关系**：主 Agent 是“项目经理（Orchestrator）”，Subagents 是“执行者（Workers）”。

```py
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent
# 创建 Tavily 客户端
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# 1. 定义一个工具函数
def internet_search(
    query: str,  # 搜索关键词
    max_results: int = 5,  # 返回结果数量
    topic: Literal["general", "news", "finance"] = "general",  # 搜索类型
    include_raw_content: bool = False,  # 是否返回原始网页内容
):
    """Run a web search"""
    return tavily_client.search( 
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

# 2. 定义一个“子智能体”（sub-agent），本质是一个配置字典
research_subagent = {
    "name": "research-agent", # 子agent的名字（内部标识）
    # 子agent的描述（主 agent 会根据这个决定是否调用它）
    "description": "Used to research more in depth questions",
    # 子agent的系统提示词（角色设定）
    "system_prompt": "You are a great researcher",
    # 子agent可用的工具
    "tools": [internet_search],
    # 指定这个子agent使用的模型（可选），不写则默认使用主agent的模型
    "model": "openai:gpt-5.2",
}

# 把子agent放进列表（因为可以有多个subagent）
subagents = [research_subagent]

# 3. 创建主agent, 传入子代理列表
agent = create_deep_agent(
    model="claude-sonnet-4-6",  # 主agent使用的模型
    subagents=subagents  		# 注册子agent（主agent可以“调用子agent”）
)
```





## Agent 的记忆

- **会话持久化 (Short-term/State)**：
  - **关键词**：`StateBackend`, **Checkpointer**。
  
  - **逻辑**：把 **GraphState** 每一秒的状态拍个快照存进数据库。
  
  - **解决**：用户刷新页面后，Agent 还能接上话吗？
  
- **长期知识库 (Long-term/Store)**：
  - **关键词**：`StoreBackend`, **InMemoryStore/PostgresStore**。
  
  - **逻辑**：从对话中提取“事实”，存入一个像图书馆一样的全局空间。
  
  - **解决**：Agent 能记住用户上个月提到的过敏史吗？
  
- **部署与多后端管理 (工程化)**
  - **内容**：**CompositeBackend (复合后端)**, **FilesystemBackend**。
  - **解决**：我的技能脚本存在硬盘，聊天记录存在数据库，用户信息存在 Redis，如何统一管理这些“分流”？



### 会话持久化（State + Checkpointer）

#### 概念

- **逻辑**：Graph 每运行一步，产生的 `GraphState` 就会被 **Checkpointer** 拍个照存起来。存下来的这个照片就叫 **State**。它对应的是 `StateBackend`。

- **解决问题**：用户刷新页面后，Agent 还能接上话吗？

  > 有时候内存里的 GraphState 会被瞬间清空（服务重启、用户关掉网页又回来等），如果没有 Checkpointer ，那么即使数据库里有用户信息，AI 也会忘了刚才聊到哪一步了。

- **==State 与 Checkpointer==**： “数据” 与 “动作”

  - **State（数据）**：那一瞬间的快照内容（比如：`{"messages": [...], "count": 1}`）。

  - **Checkpointer（执行动作）**：负责**执行**保存和读取动作的工具。

    在图运行的每个节点执行完的瞬间，自动把当前的 `GraphState` 拍张照片，存进持久化介质（如 SQLite 或 Postgres）。

- **==Checkpointer 机制==**：根据 `thread_id` 来存取数据

  当你在运行 Agent 时传入 `config = {"configurable": {"thread_id": "thread_001"}}`：

  1. **读取**：Checkpointer 会先去数据库里找：“有没有标签是 user_123 的最后一张快照？” 如果有，就把它加载进 `GraphState`。

     > 它搜寻的唯一凭证是 `config` 里的 `thread_id`。
     >
     > 在 `LangGraph` 的标准 Postgres 实现中，这张表通常叫 `checkpoints`。它存的是整个 `State` 对象的序列化（二进制）数据。

  2. **写入**：节点执行完后，Checkpointer 会更新数据库：“这是 user_123 最新的快照，请覆盖旧的。”

     > 它存的不只是最后的结果，而是**整个历史轨迹**。
     >
     > - **Checkpoint**: 当前最先进的状态。
     > - **Metadata**: 谁在什么时候操作的。
     > - **Versions**: 每一个步骤的版本号（这让你可以实现“时光倒流”，如让 Agent 回到三个步骤之前的状态）。

- **==config 和 thread_id==**：

  - **config**：一个装载运行参数（如用户名、会话ID等）的字典，它在调用 `invoke` 时作为第二个参数传入。

  - **thread_id**：`config` 里面的一个数据。

  - **config 的内容**：除了标准的 `thread_id`，你可以在 `configurable` 里塞入任何自定义的标签。

    ```py
    config = {
        "configurable": {
            "thread_id": "001",    # 框架定义必须叫这个名字才能自动存档
            "user_name": "张三",    # 自定义（可以在Node节点里通过config拿出来）
            "app_version": "v1.0"  # 自定义
        }
    }
    ```

- **==知识体系串联==**

  - **State（状态）**：对话的内容（“你好”）

  - **Backend（后端）**：存钱的银行（内存、数据库）

  - **Checkpointer（存档员）**：银行的操作员

  - **config / thread_id（配置/门牌号）**：用户在银行的**账号**

    **如果没有 `thread_id`**：存档员不知道要把这一堆 `State` 存在谁的名下，下一次用户回来时，他也找不到你的余额。

  | **环节**     | **动作**                                 | **涉及的对象**     | **物理位置**           |
  | ------------ | ---------------------------------------- | ------------------ | ---------------------- |
  | **发送请求** | 你拿着钥匙（`thread_id`）和新消息去找 AI | `config`           | **内存（瞬时参数）**   |
  | **读取存档** | 框架拿着钥匙去保险柜里搜                 | **Checkpointer**   | **数据库（索引查询）** |
  | **恢复记忆** | 框架把搜到的内容还原到大脑               | **State**          | **内存（运行中）**     |
  | **执行对话** | AI 说话，内容变多                        | **State** (更新中) | **内存（运行中）**     |
  | **保存存档** | 运行结束，框架把新大脑拍张照存回保险柜   | **Checkpointer**   | **数据库（持久化）**   |

#### 使用示例

- **创建一个包含 Checkpointer 的图并使用**：这里使用 SQLite 来存储

  ```py
  from langgraph.checkpoint.sqlite import SqliteSaver 
  from langgraph.graph import StateGraph
  
  # 1. 准备好你的“存档设备”
  # 这里可以使用内存，也可以使用真实的数据库文件
  memory = SqliteSaver.from_conn_string(":memory:") 
  
  # 2. 创建图
  workflow = StateGraph(MyAgentState)
  # ... 添加节点和边 ...
  
  # 3. 编译一个Agent，把Checkpointer挂载上去，这个图就具备了“自动存档”功能
  app = workflow.compile(checkpointer=memory)
  
  # 4. 运行Agent时，必须指定 thread_id
  config = {"configurable": {"thread_id": "thread_001"}}
  app.invoke({"messages": [("user", "你好")]}, config)
  ```

- **在 `create_deep_agent` 中怎么用**：

  当你使用 `create_deep_agent` 创建好智能体后，你在运行它时**必须**用到 `config`（前提是你配置了 `Backend`）。

  ```py
  # 1. 创建 Agent
  agent = create_deep_agent(model=llm, backend=my_backend)
  
  # 2. 第一次对话（张三）
  agent.invoke(
      {"messages": [("user", "我是张三")]},
      config={"configurable": {"thread_id": "thread_001"}}
  )
  
  # 3. 第二次对话（李四）
  # 如果 thread_id 不同，Backend 会自动开辟一个新的 State 空间
  agent.invoke(
      {"messages": [("user", "我是李四")]},
      config={"configurable": {"thread_id": "thread_002"}}
  )
  ```

- 现实使用中，怎么可能每次都指定 `thread_id`？

  在开发测试时，你确实是手动写 `thread_id: "123"`。但在**现实生产环境**中，这个过程是自动化的，通常遵循以下链路：

  1. **前端层面**：当用户打开你的聊天网页，前端程序（如 React 或 Vue）会自动生成一个 UUID，或者从浏览器的 `localStorage` 中读取之前的 `thread_id`。
  2. **后端层面**：当你点击发送，前端会把这条消息和这个 `thread_id` 一起发给你的 API 服务器（比如 FastAPI 或 Flask）。
  3. **框架层面**：你的后端代码拿到请求后，把这个 `thread_id` 填进 `config`，传给 `agent.invoke`。

  所以它不是“存在内存里自动新开”，而是由你的业务系统（你的网页或 App）来负责追踪“谁是谁”。



### 跨会话记忆（Store）

#### Store 的概念

- **逻辑**：它不随 Graph 的运行自动更新。只有当你在代码里显式说“我要存个东西”时，它才动。它对应的是 `StoreBackend`。

- **解决问题**：打破 “会话（Thread）” 的限制，实现跨会话、长期的记忆。

  > 用户在上周的 `thread_001` 对话里提到“我花生过敏”。今天用户新开了一个对话 `thread_002`。
  >
  > 因为 `Checkpointer` 是基于 `thread_id` 隔离的，`thread_002` 拿不到 `thread_001` 的存档。如果没有 `Store`，AI 又会问用户：“请问你有什么忌口吗？”

- **==store 对象==**：一个全局共享的物理实体

  - **它是全局唯一的“*存储对象*”**：在程序启动时，你定义了一个 Store 实例，决定它使用什么存储。它是单例的，像一个巨大的、连接着数据库的“书架”。

    - `store = InMemoryStore()`：存在内存

    - `store = PostgresStore(conn_pool)`：存在 DB 的 store 表

      > **Checkpoints 表**：序列化后的对话历史（二进制数据）。
      >
      > **Store 表**：简单的键值对 或 JSON，可以直接在数据库里看到 `{"hobby": "摄影"}`。

  - **它是被注入节点的“*上下文工具*”**：当图（Graph）开始运行，框架会把这个 `store` 对象 “注入” 到每一个 Node（节点）中。

    它在 Node 处理函数的 `store` 参数位上。即在 Node 函数的参数里，它表现为一个可调用的对象。可以使用用于操作数据库的 `put`、`get`、`search` 方法。

  - **它不是数据本身**，因为数据在 DB 里，Store 对象只是通往 DB 的高级网关。它记录了去哪里连数据库、用什么编码格式、是否需要加密等信息。它知道如何把你的 Python 调用翻译成 SQL 语句。

    你对它下指令（`put/get`），它利用手里的钥匙（`connection`）和翻译技巧（`serializer`）去后台（`DB`）帮你干活。

- **==store 表==**：不存原始对话，它存的是**“提取后的事实”**。

  - **Checkpointer 表存的内容**： `"User: 我叫张三，我喜欢摄影，我曾拍过很多摄影作品。"`

  - **Store 表存的内容**：

    | **行 ID** | **namespace**       | **key** | **value**          |
    | --------- | ------------------- | ------- | ------------------ |
    | 1         | `memories/user_123` | `bio`   | `{"name": "张三"}` |
    | 2         | `memories/user_123` | `hobby` | `{"like": "编程"}` |
    | 3         | `memories/user_456` | `bio`   | `{"name": "李四"}` |

  - 在一个复杂的 Agent 系统中，`Store` 表可能会被划分为不同的**顶级命名空间**：

    | **顶级命名空间 (Root)** | **第二级 (Scope)** | **存储内容示例**                                    |
    | ----------------------- | ------------------ | --------------------------------------------------- |
    | **`memories`**          | `user_id`          | 用户的姓名、忌口、过往偏好                          |
    | **`settings`**          | `user_id`          | 用户对 UI 的偏好（深色模式）、通知开关              |
    | **`docs`**              | `collection_id`    | 知识库片段（如果是做 RAG 检索）                     |
    | **`plugins`**           | `plugin_name`      | 某个特定工具运行所需的持久化数据（如 API Key 缓存） |
    | **`analytics`**         | `session_id`       | 对这场对话质量的自动化评估结果                      |

- **==存取逻辑==**

  - ***物理结构***：Namespace（命名空间），类似文件夹路径的逻辑，一个**元组 (Tuple)**，它可以无限延伸。

    一个典型的 Store 存储地址长这样： `("memories", "{user_id}", "preferences")`

    - **第一层（memories）**：大的分类，告诉后端这是记忆数据
    - **第二层（user_id）**：具体的归属人。这样 Agent 就能区分张三的记忆和李四的记忆
    - **第三层（key）**：具体的标签 `preferences`。这个标签里面的值就是用户的喜好。

  - ***存取顺序***：

    > 寻址过程：去 `store` 表里，找 `namespace` 等于 `memories/jack_001` 且 `key` 等于 `diet` 的那一行，把它的 `value` 拿出来。

    1. **根据命名空间确定 ”档案室“**：把 Namespace 拼接成一个类似文件路径的字符串或哈希值。

       > 假设 `namespace` 为 `("memories", "user_123")`。
       >
       > 拼接到 SQL 中：`SELECT * FROM store_table WHERE namespace = 'memories/user_123'`

    2. **筛选标签**：根据具体的 Key 来读取值，或进行全文搜索

       > **按 Key 读**：`store.get(namespace, "user_preference")`
       >
       > **模糊搜索**：`store.search(namespace, query="喜欢的颜色")`

    3. **序列化或反序列化**：

       - **读取（反序列化）**：Store 对象自动调用 JSON 解析器，把存在数据库中的 `{"color": "blue"}` 变回 Python 字典。

       - **存储（序列化）**：把 `("memories", "user_123")` 序列化为数据库中的 `namespace` 字段；

         → 把 Python 字典转换成 JSONB 格式；

         → 执行一条类似 `INSERT ... ON CONFLICT UPDATE` 的 SQL 语句。

  - ***读取触发的两种模式***

    - **LLM 主动调用**：用户提问 

      → LLM决策需要查看历史

      → 调用一个预设的工具，如 `search_memory(key, value)` 

      → 工具内部执行 `store.search(...)` → 工具把搜到的内容返回给 LLM

    - **框架自动预处理**：有些设计中会在 START 节点之后加一个 Pre-process 节点。

      不管用户问什么，先拿 `user_id` 去 Store 里把这个人的所有喜好捞出来。把捞到的信息塞进 `System Prompt` 告诉 LLM，让 LLM 一开始就记得用户说过的重要信息。

  - ***存储触发的两种模式***

    - **LLM 主动存储**：LLM 在对话中发现用户提到了重要信息 

      → LLM 决策需要存储记忆

      → 调用一个你预设的工具，如 `upsert_memory(key, value)` 

      → 工具内部执行 `store.put(namespace, key, value)`

    - **人工代码干预**：在图的某个节点，你用 Python 代码写死了一个逻辑，比如每当用户完成一笔交易，代码自动更新 Store 里的 `last_purchase_date`。

- **==记忆系统整体结构==**

  | **结构**         | 存储实体                                    | **内容**                      | 索引依据                 | **作用域**                   |
  | ---------------- | ------------------------------------------- | ----------------------------- | ------------------------ | ---------------------------- |
  | **GraphState**   | 内存中的一个对象（变量）                    | 整个对话历史（对象）          | 变量名                   | 运行时，仅限当前处理的这一秒 |
  | **Checkpointer** | DB 中的`checkpoints` 表（若指定了 DB 后端） | 整个对话历史（二进制或 JSON） | `thread_id`              | 短期记忆，仅限当前会话       |
  | **Store**        | DB 中的 `store` 表（若指定了 DB 后端）      | AI 提炼后的事实               | `namespace` (如 user_id) | 长期记忆，跨会话共享         |

#### 定义使用 Store 的工具

- **定义记忆工具并传给Agent**

  ```py
  def save_user_preference(key: str, value: str, config: RunnableConfig, store: BaseStore):
      """当用户提到重要的个人偏好、习惯或事实时，调用此工具记录。"""
      user_id = config["configurable"]["user_id"]
      store.put(("memories", user_id), key, {"content": value})
      return f"已记录关于 {key} 的记忆。"
  
  def load_user_memories(query: str, config: RunnableConfig, store: BaseStore):
      """当用户问起以前的事，或者你需要了解用户的历史偏好时，调用此工具搜索记忆。"""
      user_id = config["configurable"]["user_id"]
      # 在这个用户的命名空间下搜索
      memories = store.search(("memories", user_id), query=query)
      return memories
  ```

  - **工具函数的参数由什么决定**：

    - 当你在定义 `save_user_preference` 时，那个文档字符串（Docstring）和参数类型就是给 LLM 读的说明书。

      > LLM 看到用户说：“我叫张三”，它会查阅说明书，决定：`key="name"`, `value="张三"`。它是根据你的函数签名自动生成 JSON 传进去的，这就是 LLM 的“理解能力”。

    - 框架负责的部分：`config` 和 `store`，框架会自动从当前的运行环境（Runtime）中，把数据库连接对象（store）和身份配置（config）偷偷塞进这两个参数里。

- **把工具绑定到 Agent**

  ```py
  agent = create_deep_agent(
      model=llm,
      tools=[save_user_preference, load_user_memories], # 手动传入
      backend=my_backend,
  )
  ```

- **写入记忆（主动写入）**：

  1. **LLM 决策**：LLM 发现用户说了重要信息，LLM 决定调用记忆工具存储
  2. **调用 Tool**：AI 调用工具 `save_user_preference` 
  3. **Tool 执行存储**：`store.put(("memories", user_id), key, {"content": value})`

- **读取记忆**：

  - **被动读取**：LLM 决策 → 调用 Tool → Tool 执行读取
  - **主动读取**：新对话开始 → 在交给 LLM 思考之前，先去 Store 里 “捞一下”


#### 完整记忆流程

1. **外界输入**：前端带着用户消息和 `config`（包含 `thread_id` 和 `user_id`）进来。
2. **存档加载**：**Checkpointer** 拿着 `thread_id` 去 `checkpoints` 表“捞”出上一次的 `State`。
3. **图运行**：
   - **Node 执行**：LLM 思考，代码运行。
   - **State 更新**：每跑完一个 Node，`State` 变大一点。
   - **即时存档**：**Checkpointer** 每次都把变大的 `State` 覆盖回 `checkpoints` 表。
4. **长期记忆介入 (Store)**：
   - 如果 LLM 觉得：“这个信息很重要”，它调工具通过 **Store** 写入 `store` 表（跨 Thread 共享）。
   - 如果 LLM 觉得：“我要看看这人是谁”，它从 `store` 表读取以前存的键值对。
5. **结束**：返回结果给用户。此时数据库里已经存好了最新的 `State`（为了下次接话）和最新的 `Store`（为了永久记住事实）。

<img src="deepagents_memory.png" alt="deepagents_memory" style="zoom:33%;" />



## 后端与沙盒

| **后端类型**           | **物理本质**              | **适用场景**                                                 |
| ---------------------- | ------------------------- | ------------------------------------------------------------ |
| **StateBackend**       | **内存虚拟盘**            | **教学与演示**。速度极快，不花钱，但程序一关，里面的文件和记忆全丢。 |
| **StoreBackend**       | **持久化数据库/对象存储** | **轻量级生产**。能存住长期记忆和 Skills，但由于没有真实的 CPU，它**不能真跑代码**，只能存取数据。 |
| **复合型 (Composite)** | **混合动力**              | **复杂业务**。用数据库存长期记忆，用沙盒跑代码。把“脑子”和“手”分别接在最适合的地方。 |
| **远程沙箱 (Remote)**  | **云端全功能计算机**      | **重型 Agent**。比如 Modal, Runloop。它既能存文件，又能安装环境，还能高强度跑任务。 |

### 后端 `Backends`

- **作用**：提供一个 <u>**Agent 的执行环境**</u>，指定跨会话记忆的存储位置。解决问题：“当 Graph 运行完一次后，里面的数据去哪了？”

  这就是 `State`、`Store` 和 `Checkpointer` 出现的地方，它们被包裹在 `Backend` 这个参数里。

- **分类**：根据业务需求选择

  - 如果想要 “断点续传”，就去配 `StateBackend`（State+Checkpointer）
  - 如果想要 “长期记性”，就去配 `StoreBackend`（Store）

  | **后端名称**          | **物理位置**                               | **存储时长**                             | **访问限制**                                         |
  | --------------------- | ------------------------------------------ | ---------------------------------------- | ---------------------------------------------------- |
  | **StateBackend**      | **内存**（存在 LangGraph 的 state 字典里） | **临时**。对话结束或程序重启，数据就没了 | 仅限当前这一个对话线程（只能在一个对话框内聊）       |
  | **FilesystemBackend** | **硬盘**（文件夹）                         | **永久**                                 | 所有线程                                             |
  | **LocalShellBackend** | **操作系统环境**                           | 取决于你的系统设置                       | AI 可以直接通过命令行操作文件                        |
  | **StoreBackend**      | **数据库**                                 | **长久**。专门用于跨天、跨月的记忆       | 跨线程、跨用户共享（可以在不同窗口、不同设备间共享） |
  | **CompositeBackend**  | 复合                                       | 复合                                     | 复合                                                 |

- **CompositeBackend（复合后端）**：允许你把多个后端叠在一起。

  在创建代理（Agent）时，`backend` 参数通常只能接收一个对象。如果你需要同时拥有多种后端的特性，就必须使用 `CompositeBackend`（复合后端）。

  > 例如把 “技能文件夹” 设为只读的 `FilesystemBackend`
  >
  > 把 “运行时产生的数据” 设为 `StateBackend`
  >
  > 这样，AI 既能从硬盘读取本领，又不会把运行过程中的草稿纸（临时文件）乱丢到你的硬盘上。

#### StateBackend

- **适用场景**：短线、简单、安全；临时测试、Demo 演示、不需要记住历史的单次任务。

  > 处理用户的临时上传，例如用户传了一个 PDF 让 AI 总结，总结完就不用管了。

- **底层原理**：它是一个**虚拟文件系统**

  - 它没有 Store 对象，只能通过 Agent 调用 `read_file` 等工具读取。
  - 它内部自带了一个简单的 Python 字典（Dict）来模拟文件系统。你给它文件，它就直接存进自己的变量里，不依赖任何外部存储协议。

- **示例**：

  ```py
  from deepagents.backends import StateBackend
  
  agent = create_deep_agent(
      backend=StateBackend() # 默认就是这个, 可省略
  )
  ```

#### FilesystemBackend

- **适用场景**：个人工具、简单脚本、给 AI 喂外部技能

  - **轻量级本地应用**：开发一个桌面工具或个人助手，不想让用户为了运行你的程序还得去安装配置一个 PostgreSQL 数据库。智能体只在个人电脑上运行，不涉及多台服务器共享数据，文件后端是最简单的选择。
  - **插件化管理工具**：复杂项目、需要频繁增加 “技能” 的生产系统。
    - **动态扫描目录**：可以在程序运行过程中，往文件夹里丢一个新的 `search_pdf.py`，后端会让 Agent “学会”这个新本领，且无需重启程序。
    - **解耦**：如果代码里写死了 `from tools.weather import get_weather`，当你想把这个工具换成 API 调用或者存到数据库里时，你要改动大量的业务代码。 使用 Backend 只需要更改配置：
      - 今天指向 `local_folder/`（File Backend）。
      - 明天指向 `s3://bucket/skills/`（Cloud/Store Backend）。 Agent 的启动逻辑一行都不用改。
    - **权限隔离**：当 Backend 读取文件时，它可以检查：这个脚本是否有危险操作（比如删除硬盘）？这个技能是否只允许“管理员”级别的 Agent 加载？ 直接 `import` 会让这些管理逻辑变得非常混乱。

- **缺点**

  - **并发处理差**：文件通常不支持多用户同时读写。如果两个线程同时改写一个 JSON 文件，很容易导致文件损坏或数据丢失。
  - **检索性能差**：如果你想找“用户 A 在三月份的所有记忆”，程序必须把整个文件读入内存，然后遍历查找。数据量大时，速度会极慢。

- **使用格式**：

  ```py
  from deepagents.backends import FilesystemBackend
  
  agent = create_deep_agent(
      backend=FilesystemBackend(root_dir=".", virtual_mode=True)
  )
  ```

  > `root_dir` 定义 AI 可读取文件系统的根目录，`"."` 指向当前程序运行目录
  >
  > `virtual_mode=True`：是否开启 “虚拟文件系统”， `True` 不会真的改电脑文件

- **==插件化管理示例==**：

  - ***直接 Import*（硬编码方式）**：如果你想增加一个工具，必须修改 main.py 并重新启动

    ```py
    my_app/
    ├── main.py
    └── tools.py 	# 包含工具函数 get_weather
    ```

    ```py
    from tools import get_weather  # 显式导入
    from deepagents import create_deep_agent
    
    # 将工具放入列表
    tools_list = [get_weather]
    
    agent = create_deep_agent(
        model="gpt-4o",
        tools=tools_list  # 手动管理工具
    )
    ```

  - ***使用 File Backend*（插件化方式）**：

    `main.py` 不再关心具体有哪些工具，它只负责扫描文件夹。

    如果你想增加一个 “翻译” 工具，只需把 `translate.py` 丢进 `my_skills/`，不需要动 `main.py` 的代码。

    ```py
    my_app/
    ├── main.py
    └── my_skills/         # 这是一个“技能库”文件夹
        ├── weather.py     # 里面定义了 get_weather
        └── calculator.py  # 里面定义了 add_numbers
    ```

    ```py
    from deepagents.backends import FilesystemBackend
    from deepagents import create_deep_agent
    
    # 1. 定义后端，指向存放工具的目录
    skill_backend = FilesystemBackend(directory="./my_skills", virtual_mode=True)
    
    # 2. 创建 Agent，让它从后端动态加载技能
    agent = create_deep_agent(
        model="gpt-4o",
        backend=skill_backend  # Agent 启动时会自动扫描并加载目录下所有工具
    )
    ```

    > `virtual_mode=True`：安全加载，AI 只需要读取函数定义，不需要改动脚本
    >
    > 如果你想让 AI 帮你整理硬盘里的 PDF，允许 AI 真实地重命名、移动或编辑文件，那么就用 `virtual_mode=False`



#### LocalShellBackend

- **适用场景**：交互式调试，让你手动输入或查看当前的记忆状态。让 AI 直接操作你的电脑（高风险）

  > AI 自动写代码生成一个 `.py` 文件并执行它

- **示例**：

  ```py
  from deepagents.backends import LocalShellBackend
  
  agent = create_deep_agent(
      backend=LocalShellBackend(root_dir=".", env={"PATH": "/usr/bin:/bin"})
  )
  ```

  > `env={"PATH": "/usr/bin:/bin"}`：环境变量，系统去哪里找命令



#### StoreBackend

- **适用场景**：生产环境。多用户、大数据量、需要长期稳定记忆的应用。
  
  - **语义搜索**：Store 支持向量搜索（如果配置了 Embedding），这是 State 做不到的。
  - `StoreBackend` ：是一个“接口”，它会自动寻找全局对象 `store` 来执行真正的读写操作。
  
  ```py
  agent = create_deep_agent(
      backend=StoreBackend(), # 指定后端类型
      store=InMemoryStore() 	# 传入物理位置
  )
  ```
  
  
  
- **==存在内存==**：`store = InMemoryStore()`

  > **`InMemoryStore` ** 是一个符合 `LangGraph` 标准的键值对存储接口。虽然它现在在“内存”里，但它的 API（`.put`, `.get`）和真正的数据库（如 Redis 或数据库持久化存储）是一模一样的，可以理解为是一个<u>小型内存数据库</u>。

  ```py
  from langgraph.store.memory import InMemoryStore # 用于内存中存数据
  from deepagents.backends import StoreBackend # 用于定义 agent 的存储后端逻辑
  
  agent = create_deep_agent(
      # 配置后端类型
      backend=StoreBackend(
          namespace=lambda ctx: (ctx.runtime.context.user_id,),
      ),
      # 配置后端存储在哪，这里使用内存存储 (程序结束后消失)
      store=InMemoryStore() 
  )
  ```

- **==存储到数据库==**：`store = PostgresStore(conn_pool)`

  （这里使用 PostgreSQL，需先安装 `langgraph-checkpoint-postgres`

  ```py
  from langgraph.store.postgres import PostgresStore
  from psycopg_pool import ConnectionPool
  
  # 1. 建立数据库连接池
  DB_URI = "postgresql://user:password@localhost:5432/dbname"
  conn_pool = ConnectionPool(conninfo=DB_URI)
  
  # 2. 使用 PostgresStore 作为 store
  store = PostgresStore(conn_pool)
  
  # 3. 确保表结构已创建（通常在程序启动时执行一次）
  store.setup()
  
  # 4. 构建智能体
  agent = create_deep_agent(
      backend=StoreBackend(
          namespace=lambda ctx: (ctx.runtime.context.user_id,),
      ),
      store=store  # 配置后端物理位置在哪，即数据库
  )
  ```

  - `namespace=lambda ctx: (ctx.runtime.context.user_id,)`

    - **`lambda ctx: ...`**: 这是一个匿名函数。每当智能体需要读写存储时，框架都会自动把当前的 “运行上下文”（`ctx`）传进去。

    - **`ctx.runtime.context.user_id`**: 这是从当前的对话信息中提取出来的**唯一用户 ID**。

    - **`( ..., )`**: 注意这个括号和逗号，它表示一个元组。`namespace` 可以有多级，比如 `(user_id, "project_alpha", "memories")`。

  - **运行流程**：

    1. **用户 123** 发起请求；

    2. `lambda` 函数执行，计算出当前 `namespace` 是 `("user_123",)`；

    3. `StoreBackend` 只会去数据库里查询 **标签等于 `("user_123",)`** 的行。

       （即使 **用户 456** 的数据就在旁边，由于标签不匹配，智能体也看不见）

#### CompositeBackend

- **适用场景**：复杂场景。例如：短期记忆存内存（快），长期偏好存数据库（稳）。

- ==**示例1**==：使用 FilesystemBackend 动态加载脚本 + 存储数据到数据库 StoreBackend

  - **当 Agent 需要查找可用工具时**：它会去 `skills` 对应的 `FilesystemBackend` 目录下扫描 `.py` 文件。

  - **当 Agent 需要记住用户的名字时**：它会通过 `memory` 对应的 `StoreBackend` 将数据写入数据库。

  - **当你在 `./my_skills` 增加新脚本时**：Agent 无需重启，下一次任务分发时就会自动识别新技能。

  ```py
  from deepagents.backends import FilesystemBackend, StoreBackend, CompositeBackend
  from langgraph.store.postgres import PostgresStore
  from psycopg_pool import ConnectionPool
  
  # 1. 技能库：负责动态加载本地脚本
  skill_backend = FilesystemBackend(
      root_dir="./my_skills", 
      virtual_mode=True
  )
  
  # 2. 数据库：负责持久化存储（Postgres）
  pool = ConnectionPool(conninfo="postgresql://user:pass@localhost:5432/db")
  storage_backend = StoreBackend(
      store=PostgresStore(pool),
      namespace=lambda ctx: (ctx.runtime.context.user_id,)
  )
  
  # 3. 复合：把两者合二为一
  agent = create_deep_agent(
      backend=CompositeBackend(
          skills=skill_backend,    # 专门管本领
          memory=storage_backend   # 专门管记性
      )
  )
  ```

- ==**示例2**==：路由分发

  ```py
  from deepagents import create_deep_agent
  from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
  from langgraph.store.memory import InMemoryStore
  
  agent = create_deep_agent(
      # 配置后端类型
      backend=CompositeBackend(
          # 默认路由，默认的工作记忆
          default=StateBackend(),
          # 路径过滤，只要Agent尝试访问以/memories/开头的地址，复合后端就会把这个请求拦截下来，转交给StoreBackend处理
          routes={ 
              "/memories/": StoreBackend(), 
          }
      ),
      # 配置存储在哪: 使用内存存储StoreBackend
      store=InMemoryStore()  
  )
  ```

  -  **路由拦截的工作原理**：`CompositeBackend` 就像一个交通调度中心，内部维护了一张路由表。它拦截请求时，并不关心存的是什么，它只看你的**目的地地址**。

     1. **拦截请求**：当 Agent 尝试保存数据时，框架会生成一个目标路径。

        > 在 `DeepAgents` 的底层设计中，它把 Store 的命名空间（Namespace）映射成了一个字符串路径。
        >
        > **命名空间**：`("memories", "user_123")`
        >
        > **映射路径**：`/memories/user_123/`

     2. **前缀匹配**：调度中心检查这个路径

        - 如果访问的是 `/state/...`，它发现不匹配 `/memories/`，于是交给 `default`（也就是 `StateBackend`）。
        - 如果访问的是 `/memories/user_123`，它发现匹配了 `routes` 里的规则

     3. **重定向**：调度中心说：“这个地址归 `StoreBackend` 管”，然后把数据包转发给它

### 使用 Checkpointer 还是后端

#### 使用 Checkpointer 

- **作用**：手动传入 `checkpointer`，是给 Agent 接了一块 “**录音磁带**”，Agent 会把你们的对话存进去（仅当前会话）。

- **必须手动创建**：<u>如果不提供 checkpointer，系统就认为这个 Agent 不需要会话记忆</u>。

  - Agent 自动管理图，即自动管理 state 对象，而 checkpointer 的作用是把 state 的数据存到后端，你需要使用这个存储的功能就需要手动创建它。

  - 手动创建 `checkpointer` 实际上是开发者在声明：**“**我拥有这块记忆的管理权，我待会要用 `thread_id` 来操作它。”

  ```py
  from langgraph.checkpoint.memory import MemorySaver
  checkpointer = MemorySaver() # 决定checkpointer把state存储到哪里
  agent = create_deep_agent(
      model="openai:gpt-5.4",
      skills=["/skills/"],
      checkpointer=checkpointer,
      # 未指定后端则默认使用一个Statebackend
  )
  ```

- **存储到了哪里**：checkpointer 会把 state 对象数据存储到 <u>创建 checkpointer 的时候指定的位置</u>，而不是创建 Agent 时候指定的后端。

  > 上例中：`checkpointer = MemorySaver()` 决定了checkpointer 把 state 存到内存。
  >
  > 如果换成 `checkpointer = PostgresSaver(conn)`，就变成了存到数据库。

- **给 checkpointer 而不给 backend**：Agent 只能 “聊天” 并记住对话记录（checkpointer 记忆的归宿），没法 “写文件” 或 “运行代码”（Backend 干活的环境）。

#### 使用后端

- **作用**：给 Agent 创造一个 “**虚拟的 U 盘**”，它直接在当前的 Python 进程里模拟出一个文件系统。

  在这个文件系统里，无论是你喂给它的技能（Skills）、它自己总结的长期记忆、还是它亲手写下的代码，都拥有了实体的承载。

- Agent “读取技能”的行为，实际上是从这个虚拟后端里读取文件，这些文件就 “挂载” 在这个指定的后端里。

```py
```



### 典型后端配置

**<u>短期记忆 + 长期记忆 + 动态脚本配置</u>**

| **存储类型**      | **对应后端**   | **路径挂载点 (示例)**    | **核心用途**                                |
| ----------------- | -------------- | ------------------------ | ------------------------------------------- |
| **短期记忆**      | `StateBackend` | `default` (或 `/state/`) | 存储当前对话的上下文（Checkpointer）        |
| **长期记忆**      | `StoreBackend` | `/memories/`             | 存储用户信息、偏好、长期事实                |
| **动态脚本/配置** | `FileBackend`  | `/scripts/`              | 动态读取 Python 脚本、Prompt 模板或插件配置 |

```py
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FileBackend
from langgraph.store.memory import InMemoryStore
# 假设使用 Postgres 存长期记忆
# from langgraph.store.postgres import PostgresStore 

# 1. 初始化物理存储对象
long_term_store = InMemoryStore() # 也可以换成 PostgresStore

# 2. 构建复合后端
composite_backend = CompositeBackend(
    # A. 默认：存短期对话状态 (Checkpoints)
    default=StateBackend(), 
    routes={
        # B. 长期记忆：只要路径以 /memories/ 开头，就存入 Store
        "/memories/": StoreBackend(),
        
        # C. 动态脚本：只要路径以 /scripts/ 开头（虚拟路径），就去指定文件夹读文件
        # 比如你的 Python 脚本存在 './agent_scripts' 目录下（真实路径）
        "/scripts/": FilesystemBackend(directory="./agent_scripts", virtual_mode=True),
    }
)

# 3. 创建 Agent
agent = create_deep_agent(
    model=llm,
    tools=[...], 
    backend=composite_backend, # 传入后端
    store=long_term_store # 传入物理存储位置
)
```

- **==寻址逻辑==**

  - ***工具函数存取长期记忆***： 

    `store.get(("memories", "user_123"), "bio")`

    → 框架将其转化为路径 `/memories/user_123/bio`。

    → `CompositeBackend` 匹配到 `/memories/` 前缀，把请求转交给 `StoreBackend`，最终去数据库查 JSON。

  - ***执行动态脚本加载***： 

    → 在节点中访问 `/scripts/tool_a.py`

    → `CompositeBackend` 匹配到 `/scripts/` 前缀，转交给 `FilesystemBackend`，它会直接去你的硬盘读取该文件的内容。

  - ***普通对话回复***： 由于没有匹配任何特殊前缀，所有的对话历史自动流向 `default`（`StateBackend`），存入 `checkpoints` 表。

- **==虚拟路径与真实路径的映射==**

  - **Agent 为什么会访问 `/scripts/` 路径？**

    - **场景 A：你在 Prompt 中告诉了它** 

      你在 System Prompt 里写道：“如果你需要复杂的计算逻辑，请读取 `/scripts/math_tools.py` 中的函数内容。” 此时，Agent 会尝试通过工具或节点去“读”这个路径。

    - **场景 B：你的 Node 逻辑里写死了寻址** 

      你编写了一个通用的“脚本加载节点”，代码里写着：`content = backend.read("/scripts/my_script.py")`。

    Agent 不需要知道真实文件系统重脚本放在哪个文件夹下（真实路径）。它只需要知道在它的“虚拟世界” 里，所有的脚本都放在 `/scripts/` 这个路径下（虚拟路径）。

  - ***路径映射***：是 `FilesystemBackend` 的职责。当你初始化它时，实际上建立了一个映射关系：

    - **虚拟路径 (Agent 看到的)**：`/scripts/test.py`
    - **物理路径 (硬盘上的)**：`./agent_scripts/test.py`

    当 `FilesystemBackend(directory="./agent_scripts")` 接收到读取 `/scripts/test.py` 的请求时，它会：

    1. 剥离掉前缀 `/scripts/`。
    2. 把剩下的 `test.py` 拼接到 `base_dir` 后面。
    3. 最终去执行 `open("./agent_scripts/test.py")`。

  - ***意义***：部署灵活性

    > 在你的开发机上，脚本可能在 `C:\Users\Admin\agent_scripts`。
    >
    > 在服务器上，脚本可能在 `/app/data/scripts`。
    >
    > 但是你的 Agent 逻辑和 Prompt 永远只需要写 `/scripts/`。你只需要在不同环境下修改 `FilesystemBackend` 的 `directory` 参数即可，不需要改动任何 Agent 内部的代码。

- **==create_deep_agent 函数中的 store 参数==**：只有两种情况下需要传入它

  - **后端使用 StoreBackend 或 CompositeBackend**
    - **StoreBackend = 接口**：它定义了“如果有人访问这个路径，就去操作长期存储”。
    - **store 参数 = 实体**：它提供了真正的数据库操作方法（`put/get`）。
    - **CompositeBackend = 路由器**：它并不直接操作存储，但它负责把带有 `/memories/` 的请求重定向给拥有 `store` 访问权限的 `StoreBackend`。
  - 你定义的工具函数（如 `save_user_preference`）中声明了 `store: BaseStore` 参数，框架会自动把这个 `store` 注入进去。



### 沙盒 Sandbox

- **作用**：让 Agent 在隔离的环境中拥有自己的文件系统和 shell 工具

- **使用场景**：希望 Agent 写入文件、安装依赖和运行命令而不更改本地机器时 

  - 如果你想让 Agent 拥有 **“手”**，去改代码、跑测试，你选 **Modal** 或 **Runloop**。

  - 如果你想让这双“手”在任何地方都好用，你用 **Daytona** 管理环境。
  - 如果你想让这双“手”工作得透明、可追踪，你必须接入 **LangSmith**。

- **为什么不用原生 Docker 或云服务器**：

  | **维度**     | **原生 Docker / 云服务器** | **专业沙箱后端 (Modal/Runloop/Daytona)**            |
  | ------------ | -------------------------- | --------------------------------------------------- |
  | **启动速度** | 较慢，且管理复杂           | **极快**，API 一键生成                              |
  | **通信成本** | 需自己写 SSH/Socket 逻辑   | **原生 API 支持**，Agent 像调函数一样调系统         |
  | **隔离级别** | 基础隔离，容易互相干扰     | **强隔离**，每个 Agent 都有独立的文件系统和进程空间 |
  | **可观测性** | 需自己装监控软件           | **内置监控（LangSmith 对接）**，每行命令都有日志    |

  

#### Modal（快速单次运行）

- **本质**：<u>让 “本地函数” 运行在云端，用于快速运行 AI 计算任务</u>。

  - 当你运行 Modal 代码时，代码会被瞬间打包，发送到 Modal 的服务器集群中，在几秒钟内拉起一个容器执行。
  - 它通常是 **无状态** 的（Task 结束就没了）。侧重于输入 → 处理 → 输出。

  - 这个沙箱是有 **IP 地址** 和 **文件系统** 的。Agent 在里面执行的操作，都是真实发生在那台云端机器上的。

- **沙盒特点**：非常底层，需要自定义环境。适用于：<u>图像生成、重型数据处理</u>。

- **==让 Agent 使用 Modal 沙箱==**

  ```
  pip install langchain-modal
  ```

  ```py
  import modal  # 导入modal库，用于管理远程运行环境（类似云函数/容器）
  from deepagents import create_deep_agent  
  from langchain_anthropic import ChatAnthropic  # 用于调用Claude模型
  from langchain_modal import ModalSandbox  # 导入Modal沙箱封装，用于在Modal环境中执行代码
  
  # Agent连上云端，查找名为"your-app"的Modal应用蓝图（必须提前创建好）
  # 这个蓝图里规定了用什么系统、装了什么软件
  app = modal.App.lookup("your-app")
  
  # Modal根据蓝图，在云端真实地创建了一台微型虚拟机（容器，沙箱环境）。
  modal_sandbox = modal.Sandbox.create(app=app)
  
  # 框架把这台“云端虚拟机”（Modal沙箱）包装成统一接口（backend），供Agent调用
  modal_backend = ModalSandbox(sandbox=modal_sandbox)
  
  # 创建一个agent
  agent = create_deep_agent(
      model=ChatAnthropic(model="claude-sonnet-4-6"),
      system_prompt="You are a Python coding assistant with sandbox access.", 
      backend=modal_backend,  # 指定代码执行环境为Modal沙箱
  )
  
  try:  # 调用agent执行任务
      result = agent.invoke(
          {
              "messages": [  # 输入对话消息列表
                  {
                      "role": "user",  # 用户角色
                      "content": "Create a small Python package and run pytest",  # 用户消息：创建Python包并运行测试
                  }
              ]
          }
      )
  finally:  # 无论是否出错，最后都关闭沙箱，释放资源
      modal_sandbox.terminate()
  ```

- **==创建 Modal 应用==**：

  - **方式 1：在代码中实时定义（最常用）**

    这是你开发 Agent 时最常见的写法。你不需要去网页上点点画画，直接在 Python 文件里写：

    ```py
    import modal
    
    # 1. 定义环境（镜像）:比如你需要这个沙箱里自带 pandas 和 pytest
    image = modal.Image.debian_slim().pip_install("pandas", "pytest")
    
    # 2. 创建 App 对象: 这里的 "my-agent-app" 就是你之后 lookup 时要用的名字
    app = modal.App("my-agent-app", image=image)
    
    # 3. 如果你想把这个 App 部署到云端，让它持久存在
    # 在终端运行：modal deploy your_script.py
    ```

  - **方式 2：在终端（CLI）提前部署**

    当你运行 `modal deploy` 后，Modal 会在云端注册这个 `App`。

    一旦部署成功，你的 Agent 代码就可以通过： `app = modal.App.lookup("my-agent-app")` 随时随地“召唤”这个云端环境，而不需要在 Agent 代码里重新定义镜像。

  - **查看我的 Modal 云服务**：[modal.com](https://modal.com)

    当你使用 `modal deploy` 部署后，它就不再依赖你的本地电脑。

    登录 Modal 官网后台，你会看到一个 **"Apps"** 标签页，在这里可以看到所有部署好的 **Apps** 蓝图、正在运行的 **Sandboxes**（沙箱）以及实时日志（Logs）。



#### Runloop（持久环境）

- **本质**：它是一个**持久化的完整的 Linux 环境**，预装了各种开发工具（Python, Git, Docker, Node.js 等）。

  - **持久性**：它解决了 “断电丢失” 的问题。如果你在 Runloop 开启了一个环境，Agent 在里面写了一半的代码，即便对话断了，下次连接时那个环境还在，文件也还在。

    > 普通的沙盒往往运行完一段代码就自毁了。而 Runloop 认为，Agent 需要一个**持久的、可以反复进入**的 “办公桌”。哪怕 Agent 思考了 1 分钟再回来，桌上的文件和运行中的进程依然在那里。

  - **适用于**：<u>AI 程序员、自动化运维、长期运行的任务</u>。

  - **创建**：调用 `client.devbox.create()` 时，系统会在几秒钟内在 Runloop 的云端集群里拉起一个轻量级的虚拟机。

  - **Runloop 的管理页面**： [runloop.ai](https://runloop.ai) 

- **使用 Runloop 沙箱**

  ```
  pip install langchain-runloop
  ```

  ```py
  import os  
  from deepagents import create_deep_agent  
  from langchain_anthropic import ChatAnthropic  # 用于调用Claude模型
  from langchain_runloop import RunloopSandbox  # 导入Runloop沙箱，用于在隔离环境中执行代码
  from runloop_api_client import RunloopSDK  # 导入Runloop SDK客户端，用于与Runloop服务通信
  
  # 创建Runloop客户端，通过环境变量里的API Key向Runloop服务器发起身份验证
  client = RunloopSDK(bearer_token=os.environ["RUNLOOP_API_KEY"])
  
  # 创建一个云端的开发环境（Runloop的云端准备好了一台Linux环境）
  devbox = client.devbox.create()
  
  # 创建一个沙箱执行环境，供Agent使用
  runloop_backend = RunloopSandbox(devbox=devbox)
  
  # 创建一个agent
  agent = create_deep_agent(
      model=ChatAnthropic(model="claude-sonnet-4-6"),  
      system_prompt="You are a Python coding assistant with sandbox access.", 
      backend=runloop_backend,  # 指定runloop沙箱后端为代码执行环境
  )
  
  try:   # 调用agent执行任务
      result = agent.invoke(
          {
              "messages": [  
                  {
                      "role": "user",  # 表示这是用户输入
                      "content": "Create a small Python package and run pytest",  # 让agent创建Python包并运行测试
                  }
              ]
          }
      )
  finally:   # 无论是否出错，最后都关闭远程开发环境，避免资源泄漏
      devbox.shutdown()
  ```

  

#### Daytona（标准化环境）

- **本质**：一个开源的 **标准化开发环境（SDE）管理平台**。

  - **标准样板房**：确保每个 Agent 的办公环境配置都整齐划一，方便大规模部署。

    它是跨平台的。不管是在你的笔记本上，还是在 Azure 上，Agent 面对的环境都是一模一样的（DevContainer 标准）。

  - **可云也可本地部署**：可以把 Daytona 部署在自己的阿里云、腾讯云甚至公司机房内网里，Daytona 都能一键拉起一个符合 VS Code 标准的开发环境。
  - **持久化**：Agent 下班了（进程结束），`sandbox.stop()` 只是关机。下次 `Daytona().create()`，之前写的代码、下载的 npm 包都还在那个 Volume（卷）里。

- **控制台**：

  - **本地版**：在本地运行 `daytona server`，浏览器打开 `localhost:3000` 就能看到。
  - **云端版**：访问 [daytona.io](https://www.daytona.io) 登录 Dashboard。

- **为什么需要 Daytona？**

  1. **环境对齐**：Agent 在沙盒里跑代码的环境，可以和你电脑上的 VS Code 环境完全一模一样（通过 `devcontainer.json`）。
  2. **安全性**：企业不敢把代码发到外部云（Modal/Runloop）。Daytona 允许企业在自己的内网里起沙箱，数据不出库。
  3. **多并发**：它支持 Agent “开分身”。一个 Agent 遇到难题，可以瞬间克隆（Fork）出 10 个一模一样的环境去尝试 10 种修复方案。

- **使用 Daytona**

  ```
  pip install langchain-runloop
  ```

  ```py
  from daytona import Daytona  # 导入Daytona客户端，用于创建远程开发环境
  from deepagents import create_deep_agent  
  from langchain_anthropic import ChatAnthropic  
  from langchain_daytona import DaytonaSandbox  # 导入Daytona沙箱封装，用于执行代码
  
  # 创建一个Daytona沙箱环境（远程隔离运行环境）
  sandbox = Daytona().create()
  # Daytona() 会根据你的本地配置（通常是 ~/.daytona/config）自动寻找连接目标。如果你已经登录了云端，它就连云端。
  
  # 将Daytona沙箱包装成统一接口，供agent使用
  backend = DaytonaSandbox(sandbox=sandbox)
  
  # 创建agent
  agent = create_deep_agent(
      model=ChatAnthropic(model="claude-sonnet-4-6"),  
      system_prompt="You are a Python coding assistant with sandbox access.", 
      backend=backend,  # 指定代码执行环境（Daytona沙箱）
  )
  
  try:  # 调用agent执行任务
      result = agent.invoke(
          {
              "messages": [  
                  {
                      "role": "user", 
                      "content": "Create a small Python package and run pytest", 
                  }
              ]
          }
      )
  finally:   # 无论是否报错，最后都关闭沙箱，释放资源（避免占用/计费）
      sandbox.stop()
  ```

- **Daytona 的部署**：由本地配置决定部署在哪里

  当运行 `pip install daytona` 并执行 `daytona profile set` 时，你在本地电脑上指定了连接目标。

  - 如果你指向 `localhost`，`Daytona().create()` 就在你本地的 Docker 里开沙箱。
  - 如果你指向你的 **私有云服务器 IP**，它就在那台服务器上开沙箱。
  - 如果你指向 **Daytona Cloud**，它就在官方的云端开沙箱。

  对 Agent 代码来说，它只管调用 `.create()`，至于这台“电脑”是在哪里，Agent 并不感知。

  

#### LangSmith（监控+沙箱）

- **本质**：[LangSmith](https://smith.langchain.com/)

  - **调试监视器（Observability/Tracing）**：它记录 Agent 思考的每一步、每一个工具调用、花了多少钱、哪里报错了。

    你可以在 LangSmith 里回溯 Agent 在 Modal 或 Runloop 里执行的每一个细节。

  - **沙盒（Sandboxing）** ：这是它后来推出的功能。它提供一个**原生集成**的隔离环境来运行 Agent 的代码。

    - **无缝追踪 (Deep Integration)**： 当 Agent 在 LangSmith 沙盒里运行代码时，代码的 Stdout（标准输出）、Stderr（报错信息） 会自动出现在 LangSmith 的 Trace 图表 中。你不需要手动写任何日志代码，监控和执行是合二为一的。
    - **从追踪到测试的闭环**： 如果在沙盒里运行失败了，你可以直接在 LangSmith 网页上把这个失败案例点击 “添加到测试集（Dataset）”，以后每次修改代码都能自动跑一遍这个测试。

- **使用 LangSmith**

  ```
  pip install "langsmith[sandbox]"
  ```

  ```py
  from deepagents import create_deep_agent  
  from langchain_anthropic import ChatAnthropic 
  from deepagents.backends import LangSmithSandbox  # 导入LangSmith沙箱封装
  from langsmith.sandbox import SandboxClient  # 导入LangSmith沙箱客户端，用于创建/管理沙箱
  
  # 创建LangSmith沙箱客户端（用于和LangSmith服务通信）
  # 通过你配置的LANGSMITH_API_KEY连接到LangSmith的云端服务器
  client = SandboxClient()
  
  # 远程创建一个沙箱环境，基于指定模板
  # my-template是你提前在LangSmith后台定义的“镜像”
  ls_sandbox = client.create_sandbox(template_name="my-template")
  
  # 将LangSmith沙箱包装成统一接口，供agent执行代码 
  backend = LangSmithSandbox(sandbox=ls_sandbox)
  
  # 创建agent
  agent = create_deep_agent(
      model=ChatAnthropic(model="claude-sonnet-4-6"), 
      system_prompt="You are a Python coding assistant with sandbox access.",  
      backend=backend,  # 指定代码执行环境（LangSmith沙箱）
  )
  
  try:# 调用agent执行任务（invoke是统一入口方法）
      result = agent.invoke(
          {
              "messages": [ 
                  {
                      "role": "user",
                      "content": "Create a small Python package and run pytest",
                  }
              ]
          }
      )
  finally: # 删除沙箱（根据名称删除），释放资源 
      client.delete_sandbox(ls_sandbox.name)
  ```



## skills 和 memory

### `skills` 参数

- **Skill（SKILL.md）**：是对 Tool 的高级封装和逻辑指导。
  - 用于告诉 Agent “作为一名员工，你应该如何**组合**使用你的设备”。
  - 专注于**任务逻辑、风格和边界**。
  - **为什么要在这里约束？**：
    - 因为一个 Tool 往往是通用的（如搜索），而 Skill 是具体的（如 “气象分析技能”）。
    - 在 Skill 里，你可以写：“当执行天气查询时，必须先查时间，再查天气，最后输出 5 天预报。”
  - **区别**：Tool 说明是 **“怎么开关灯”**，Skill 是 **“什么时候该开灯，以及开灯后要看什么”**。

#### Statebackend

从网络下载 Skills 文件并使用

- **指定文件方式**：

  1. `create_deep_agent` 中用 `skills` 参数指定技能目录路径：定义 Agent 的“视野范围”

     > 告诉 Agent：“去你的仓库管理系统里查看以 `/skills/` 开头的所有记录，那些是你的技能。”
     >
     > 它在逻辑上激活了 Agent 扫描该目录的权限。

  2. 运行时通过 `agent.invoke()` 注入具体文件：提供“物理实体”

     > 在调用（Invoke）时传入的 `files`，是真真实实地在内存文件系统里**创建**了这个文件。

- **Agent 是怎么找到技能的？**

  1. **启动**：Agent 接收到任务
  2. **检查配置**：Agent 发现配置了 `skills=["/skills/"]`
  3. **扫描动作**：Agent 尝试去访问后端（Backend）的 `/skills/` 路径
  4. **物理匹配**：如果此时后端（通过你传入的 `files`）刚好在 `/skills/langgraph-docs/SKILL.md` 有数据，Agent 就能顺利读到
  5. **如果路径不匹配**：如果你在 `skills` 里写了 `/skills/`，但在 `files` 里把文件存在了 `/temp/SKILL.md`，Agent 就会因为“找不到手册”而罢工

  ```py
  from deepagents import create_deep_agent  
  from urllib.request import urlopen  # 用于从网络下载文件内容（HTTP请求）
  from deepagents.backends.utils import create_file_data  # 导入工具函数，用于把文件内容转换为agent可识别的数据结构
  from langgraph.checkpoint.memory import MemorySaver  # 导入内存型checkpoint，用于保存对话/状态
  
  # 创建一个内存型checkpoint，用于保存agent的执行状态（例如对话上下文）
  checkpointer = MemorySaver()
  
  # 定义技能文件的URL地址（远程的SKILL.md文件） 
  skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/cli/examples/skills/langgraph-docs/SKILL.md"
  
  # 从远程下载技能文件内容
  with urlopen(skill_url) as response:  # 发起HTTP请求获取文件
      skill_content = response.read().decode('utf-8') # 读取并转成字符串
  
  # 构造文件：一个键值对，包括路径 + 内容
  skills_files = { 	
      "/skills/langgraph-docs/SKILL.md": create_file_data(skill_content)  
  }
  
  # 创建agent
  agent = create_deep_agent(
      model="openai:gpt-5.4",  
      skills=["/skills/"],  # 指定技能目录
      checkpointer=checkpointer,  # 指定状态保存机制（MemorySaver）
  )
  
  # 调用agent执行任务
  result = agent.invoke(
      {
          "messages": [  # 输入对话消息
              {
                  "role": "user",  # 用户角色
                  "content": "What is langgraph?",  # 提问
              }
          ],
          "files": skills_files  # 传入文件内容
      },
      config={
          "configurable": {
              "thread_id": "12345"  # 指定会话ID，用于区分不同对话（checkpointer）
          }
      },
  )
  ```

  - **文件挂载**：通过网络下载的 `skills_files` 并将这些文本包装成虚拟文件。由于你没有指定 `backend`，`create_deep_agent` 自动在内存中启动了一个 `StateBackend`，并将这些文件“塞”了进去。
  - **记忆**：提供一个存在 `MemorySaver()` 的 checkpointer，在内存里开辟了一块空间，让 Agent 记得对话记录。
  - **生命周期**： Checkpointer（对话存档） 和 StateBackend（执行环境） 都在内存里：
    - **程序运行时**：它表现得像个专业的 AI 助手，懂技能、记历史。
    - **程序关闭后**：所有的技能文件、聊天记录、生成的临时数据全部消失，不留一点痕迹。

#### StoreBackend

从网络下载 Skills 文件并使用

- **指定文件方式**： 

  1. 使用 `store.put` 注入文件内容（键值对形式）到存储型后端：在物理层里存放一份真实的数据

  2. `create_deep_agent` 中用 `skills` 参数指定技能目录路径：定义 Agent 的“视野范围”

     > 告诉 Agent：“去你的仓库管理系统里查看以 `/skills/` 开头的所有记录，那些是你的技能。”

  3. `create_deep_agent` 中传入这个 `store`

- **Agent 是怎么找到技能的？**

  1. **加载**： Agent 启动后，读取 `skills` 参数，知道自己需要寻找 `/skills/` 路径下的技能。
  2. **寻址**： Agent 询问 `StoreBackend`：“我有 `/skills/` 路径下的东西吗？”
  3. **转换**： `StoreBackend` 收到请求，它知道自己对接的是 `store`。它会自动加上 `("filesystem",)` 这个命名空间前缀，然后去 `store` 字典里查找。
  4. **读取**： `store.get` 找到了你之前 `put` 进去的数据。
  5. **注入**： 文件内容被提取出来。Agent 看到 `SKILL.md`，理解了里面的提示词，从而“学会”了如何调用相关工具。

  ```py
  from deepagents import create_deep_agent  
  from deepagents.backends import StoreBackend  
  from urllib.request import urlopen  # 导入urlopen，用于从网络下载远程文件
  from deepagents.backends.utils import create_file_data  # 导入工具函数，将文本转为文件数据格式
  from langgraph.store.memory import InMemoryStore  # 导入内存存储（模拟文件系统）
  
  # 创建一个内存存储对象（用于存储虚拟文件）
  store = InMemoryStore()
  
  # 定义技能文件的远程地址（SKILL.md）
  skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/cli/examples/skills/langgraph-docs/SKILL.md"
  
  # 从远程下载技能文件内容
  with urlopen(skill_url) as response:  # 发起HTTP请求
      skill_content = response.read().decode('utf-8')  # 读取并转成字符串
  
  # 将技能文件写入store中（模拟文件系统）
  store.put(
      namespace=("filesystem",),  # 命名空间（固定写法，表示文件系统）
      key="/skills/langgraph-docs/SKILL.md",  # 文件路径（必须以/开头）
      value=create_file_data(skill_content)  # 文件内容（包装成标准格式）
  )
  
  # 创建agent
  agent = create_deep_agent(
      model="openai:gpt-5.4",  
      backend=StoreBackend(), 	# 指定后端类型使用StoreBackend
      store=store,  				# 传入后端物理位置
      skills=["/skills/"]  		# 指定技能目录（agent会扫描该目录下的SKILL.md）
  )
  
  # 调用agent执行任务
  result = agent.invoke(
      {
          "messages": [  # 输入对话
              {
                  "role": "user",  # 用户角色
                  "content": "What is langgraph?",  # 提问内容
              }
          ]
      },
      config={
          "configurable": {
              "thread_id": "12345"  # 会话ID（用于区分不同对话上下文）
          }
      },
  )
  ```

- 先建了一个图书馆（Store），然后告诉 Agent 如何通过管理员（StoreBackend）去借书（Skills）
  - **使用存储后端（这里是内存型）**：一旦 Python 脚本停止，`store` 对象被销毁，所有的技能文件也随之消失。
  - **没有 Checkpointer**：没有对话记忆

#### FilesystemBackend

- **人机参与**：[跳转](#人机参与)

  ```py
  from deepagents import create_deep_agent  
  from langgraph.checkpoint.memory import MemorySaver  # 导入内存型checkpoint
  from deepagents.backends.filesystem import FilesystemBackend  # 导入文件系统后端（直接操作本地文件）
  
  # 创建checkpoint对象（用于保存状态） 
  checkpointer = MemorySaver()
  
  # 创建agent
  agent = create_deep_agent(
      model="openai:gpt-5.4", 
      backend=FilesystemBackend(root_dir="/Users/user/{project}"),  # 指定本地文件系统根目录（agent可读写这里）
      skills=["/Users/user/{project}/skills/"],  # 指定技能目录（本地路径）
      
      # 设置哪些操作需要“人工确认”（human-in-the-loop） 
      interrupt_on={
          "write_file": True,   # 写文件需要人工确认（可批准 / 修改 / 拒绝）
          "read_file": False,   # 读文件不需要中断（直接执行）
          "edit_file": True     # 编辑文件需要人工确认
      },
      
      checkpointer=checkpointer,  # 传入checkpoint
  )
  
  # 调用agent执行任务
  result = agent.invoke(
      {
          "messages": [  # 输入对话
              {
                  "role": "user",  # 用户角色
                  "content": "What is langgraph?",  # 提问内容
              }
          ]
      },
      config={
          "configurable": {
              "thread_id": "12345"  # 会话ID（用于区分不同会话状态）
          }
      },
  )
  ```

### `memory` 参数

- **作用**：指定 “用户定义的上下文文件”，是<u>纯文本参考资料</u>（如 `.md`, `.txt`, `.json`）

  - 它告诉 Agent：除了你的大脑（LLM）和你的工具（Skills），这里还有一些知识背景（关于当前任务背景、历史记录或特定实体信息的文件），你必须优先参考它们。

  - **在哪里**：存在于 **Agent 后端 (Backend)**。如果没有显式指定 `backend`，它默认存在内存里的 `StateBackend`。

  - **传递**：在 `create_deep_agent` 的 `memory` 参数中指定文件路径 + <u>在 `agent.invoke()` 中注入具体文件</u>

    - `memory=["/AGENTS.md"]` 是 **“寻找指令”**（告诉它看哪）

    - `invoke(files=...)` 是 **“实体供应”**（把东西给它），这是 <u>运行期注入</u>，仅对当前请求有效。

      > 运行期注入：可以实现**动态上下文**，如每个用户的请求可能对应不同的文档（比如 A 用户问 A 订单，B 用户问 B 订单）、或你想要临时给 Agent 传递一些只对当前这轮对话有效的最新数据。

#### **StateBackend**

- **指定文件方式**：

  1. `memory=["/AGENTS.md"]` ：定义 Agent 的“视野范围”，告诉它这里有参考资料
  2. 运行时通过 `agent.invoke()` 注入具体文件：提供“物理实体”


  ```py
  from urllib.request import urlopen  
  from deepagents import create_deep_agent  
  from deepagents.backends.utils import create_file_data  
  from langgraph.checkpoint.memory import MemorySaver  # 导入内存型checkpoint
  
  # 从远程下载AGENTS.md文件（作为memory文件）
  with urlopen("https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/examples/text-to-sql-agent/AGENTS.md") as response:  # 发起HTTP请求
      agents_md = response.read().decode("utf-8")  # 读取并解码为字符串
  
  # 创建checkpoint对象
  checkpointer = MemorySaver()
  
  # 创建agent
  agent = create_deep_agent(
      model="openai:gpt-5.4", 
      memory=[ # 指定memory文件路径（agent会把这些文件当作“长期记忆”使用）  
          "/AGENTS.md"
      ],
      checkpointer=checkpointer,  # 传入checkpoint
  )
  
  # 调用agent执行任务
  result = agent.invoke(
      {
          "messages": [  # 输入对话
              {
                  "role": "user",  # 用户角色
                  "content": "Please tell me what's in your memory files.",  # 让agent读取memory内容
              }
          ],
          # 初始化虚拟文件系统（将AGENTS.md注入进去）  
          "files": {
              "/AGENTS.md": create_file_data(agents_md)  # 文件路径必须和memory中一致
          },
      },
      config={
          "configurable": {
              "thread_id": "123456"  # 会话ID
          }
      },
  )
  ```

#### StoreBackend

- **指定文件方式**：

  1. 使用 `store.put` 注入文件内容（键值对形式）到存储型后端：在物理层里存放一份真实的数据
  2. `create_deep_agent` 中用 `memory` 参数指定目录路径：定义 Agent 的“视野范围”
  3. `create_deep_agent` 中传入这个 `store`

  ```py
  from urllib.request import urlopen  
  from deepagents import create_deep_agent 
  from deepagents.backends import StoreBackend  
  from deepagents.backends.utils import create_file_data 
  from langgraph.store.memory import InMemoryStore  # 导入内存存储
  
  # 从远程下载AGENTS.md文件内容（作为memory文件）
  with urlopen("https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/examples/text-to-sql-agent/AGENTS.md") as response:  # 发起HTTP请求
      agents_md = response.read().decode("utf-8")  # 读取并解码为字符串
  
  # 创建内存存储【文件存储位置】
  store = InMemoryStore()
  
  # 将文本内容转换为标准文件数据格式 
  file_data = create_file_data(agents_md)
  
  # 将文件写入store中（模拟文件系统）
  store.put(
      namespace=("filesystem",),  # 命名空间，表示文件系统（固定写法）
      key="/AGENTS.md",  # 文件路径（必须与memory配置一致）
      value=file_data  # 文件内容
  )
  
  # 创建agent
  agent = create_deep_agent(
      model="openai:gpt-5.4",  
      backend=StoreBackend(),  # 使用StoreBackend，从store中读取文件
      store=store,  # 传入存储对象
      # 指定memory文件路径（agent会把它当作长期记忆） 
      memory=[
          "/AGENTS.md"
      ]
  )
  
  # 调用agent执行任务
  result = agent.invoke(
      {
          "messages": [  # 输入对话
              {
                  "role": "user",  # 用户角色
                  "content": "Please tell me what's in your memory files.",  # 让agent读取memory内容
              }
          ],
          # 初始化虚拟文件系统（再次注入文件，确保可访问） 
          "files": {
              "/AGENTS.md": create_file_data(agents_md)  # 路径必须与memory一致
          },
      },
      config={
          "configurable": {
              "thread_id": "12345"  # 会话ID（用于区分不同上下文）
          }
      },
  )
  ```

#### FilesystemBackend

- **人机参与**：[跳转](#人机参与)

  ```py
  from deepagents import create_deep_agent
  from deepagents.backends import FilesystemBackend
  from langgraph.checkpoint.memory import MemorySaver
  
  checkpointer = MemorySaver()
  
  agent = create_deep_agent(
      model="openai:gpt-5.4",
      backend=FilesystemBackend(root_dir="/Users/user/{project}"),
      memory=[
          "./AGENTS.md"
      ],
      interrupt_on={
          "write_file": True,  # Default: approve, edit, reject
          "read_file": False,  # No interrupts needed
          "edit_file": True    # Default: approve, edit, reject
      },
      checkpointer=checkpointer,  # Required!
  )
  ```



## 其他

### <a name="人机参与">人机参与</a>

- 有些工具操作可能比较敏感，需要人工批准才能执行。您可以为每个工具配置审批：

  可以在工具调用时为代理和子代理配置中断，也可以在工具调用内部设置。

  ```py
  from langchain.tools import tool
  from deepagents import create_deep_agent
  from langgraph.checkpoint.memory import MemorySaver
  
  @tool
  def delete_file(path: str) -> str:
      """Delete a file from the filesystem."""
      return f"Deleted {path}"
  
  @tool
  def read_file(path: str) -> str:
      """Read a file from the filesystem."""
      return f"Contents of {path}"
  
  @tool
  def send_email(to: str, subject: str, body: str) -> str:
      """Send an email."""
      return f"Sent email to {to}"
  
  # Checkpointer is REQUIRED for human-in-the-loop
  checkpointer = MemorySaver()
  
  agent = create_deep_agent(
      model="claude-sonnet-4-6",
      tools=[delete_file, read_file, send_email],
      interrupt_on={
          "delete_file": True,  # Default: approve, edit, reject
          "read_file": False,   # No interrupts needed
          "send_email": {"allowed_decisions": ["approve", "reject"]},  # No editing
      },
      checkpointer=checkpointer  # Required!
  )
  ```

### 结构化输出

使用 `create_deep_agent()` 的 `response_format` 参数。

```py
import os 
from deepagents import create_deep_agent  
from typing import Literal  # 导入Literal类型，用于限制参数只能取固定值
from pydantic import BaseModel, Field  # 导入Pydantic，用于定义结构化数据模型
from tavily import TavilyClient  # 导入Tavily客户端（用于联网搜索）

# 创建Tavily客户端，从环境变量中读取API Key 【联网搜索能力】
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# 定义一个工具函数：用于执行互联网搜索 【提供给agent的tool】
def internet_search(
    query: str,  # 搜索关键词（必须参数）
    max_results: int = 5,  # 最大返回结果数量（默认5）
    topic: Literal["general", "news", "finance"] = "general",  # 搜索主题（限制取值范围）
    include_raw_content: bool = False,  # 是否返回原始网页内容（默认不返回）
):
    """Run a web search"""  # 工具说明（agent会看到这个描述）
    
    # 调用Tavily搜索接口，并传入参数
    return tavily_client.search(
        query,  # 搜索关键词
        max_results=max_results,  # 返回结果数量
        include_raw_content=include_raw_content,  # 是否包含原始内容
        topic=topic,  # 搜索主题
    )

# 定义一个结构化输出模型（天气报告） 【约束agent输出格式】
class WeatherReport(BaseModel):
    """A structured weather report with current conditions and forecast."""
    location: str = Field(description="The location for this weather report")  
    temperature: float = Field(description="Current temperature in Celsius") 
    condition: str = Field(description="Current weather condition (e.g., sunny, cloudy, rainy)")  
    humidity: int = Field(description="Humidity percentage")  
    wind_speed: float = Field(description="Wind speed in km/h")
    forecast: str = Field(description="Brief forecast for the next 24 hours")  

# 创建agent
agent = create_deep_agent(
    model="openai:gpt-5.4",  # 指定使用的模型
    response_format=WeatherReport,  # 指定输出必须符合WeatherReport结构 【结构化输出】
    tools=[internet_search]  # 注册工具（agent可以调用internet_search进行搜索）
)

# 调用agent执行任务
result = agent.invoke({
    "messages": [{  # 输入对话
        "role": "user",  # 用户角色
        "content": "What's the weather like in San Francisco?"  # 提问天气
    }]
})

# 打印结构化结果（Pydantic对象）
print(result["structured_response"])  # 输出WeatherReport对象（字段已解析）
# 示例输出：
# location='San Francisco, California' temperature=18.3 condition='Sunny' humidity=48 wind_speed=7.6 forecast='...'
```

