results = {  # 整体是一个 dict（字典）≈ Java 的 Map

    'messages': [  # key="messages"，value 是一个 list（列表）≈ ArrayList

        # ===== 第1个元素：用户消息 =====
        HumanMessage(  # 一个对象（用户消息对象）
            content='你能做什么',  # 用户输入的内容
            additional_kwargs={},  # 额外参数（这里为空，通常用于扩展）
            response_metadata={},  # 响应元数据（用户消息一般为空）
            id='b052264d-a9ce-4d28-b80e-4c63a24527d8'  # 这条消息的唯一ID
        ),

        # ===== 第2个元素：AI回复 =====
        AIMessage(  # 一个对象（AI回复对象）
            content='我能帮你完成各种任务，包括：\n\n## 文件操作\n...',  
            additional_kwargs={
                'refusal': None  # 是否拒绝回答（None表示没有拒绝）
            },
            response_metadata={  # 模型返回的元数据
                'token_usage': {  # token使用情况（计费 / 性能分析用）
                    'completion_tokens': 282,  # AI生成用了多少 token
                    'prompt_tokens': 5864,  # 输入用了多少 token
                    'total_tokens': 6146,  # 总 token 数
                    'completion_tokens_details': None,  # 细节（一般不用）
                    'prompt_tokens_details': {
                        'audio_tokens': None,
                        'cached_tokens': 0  # 是否命中缓存
                    },
                    'prompt_cache_hit_tokens': 0,  # 命中缓存的 token
                    'prompt_cache_miss_tokens': 5864  # 未命中的 token
                },
                'model_provider': 'deepseek',  # 使用的模型提供商
                'model_name': 'deepseek-chat',  # 使用的模型名称
                'system_fingerprint': 'fp_xxx',  
                # 模型版本指纹（调试 / 版本追踪用）
                'id': '45453e1d-24ae-468f-8761-3183d4b3d015',  
                # 这次调用的唯一ID
                'finish_reason': 'stop',  
                # 停止原因（stop = 正常结束）
                'logprobs': None  # 概率信息（一般不开启）
            },

            id='lc_run--019d718e-8e8d-76b3-a54a-dc3206cff965-0',  
            # LangChain / Agent 运行ID
            tool_calls=[],  # 工具调用列表（为空 = 没调用工具）
            invalid_tool_calls=[],  # 无效工具调用（一般为空）
            usage_metadata={  # 和 token_usage 类似（另一种统计）
                'input_tokens': 5864,  # 输入 token
                'output_tokens': 282,  # 输出 token
                'total_tokens': 6146,  # 总 token
                'input_token_details': {
                    'cache_read': 0  # 缓存读取情况
                },
                'output_token_details': {}
            }
        )

    ]  # messages 列表结束

}  # 整个 dict 结束