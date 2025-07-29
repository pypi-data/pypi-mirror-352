from typing import Any, Dict

class IntentRecognizer:
    """
    意图识别器，用于根据用户输入和上下文信息识别用户意图
    """
    def format_prompt(self, user_input: str, tools: Any, context: str='', tips: str='', **kwargs: Dict[str, Any]):
        prompt = """
你是一个专业的意图识别助手，需要根据以下输入信息，推理用户意图并输出结构化 JSON 结果。

# 输入信息包括：
- tools：工具列表。每个工具包含：
  - name：工具名称
  - description：功能描述
  - parameters：符合 OpenAPI JSON Schema 格式，包含：
    - properties：参数名称及类型
    - required：必选参数名称列表（如为空则全为可选）

- context：历史对话信息（上下文）
- user_input：用户的最新输入消息

# 你的任务：
1. 理解 user_input + context，推断用户真实意图
2. 选择适当的工具组成工具链（tool_chain）来满足用户意图
3. 为每个工具提取参数（未提供的设置为 null），区分：
   - required_parameters：来源于 parameters.required
   - optional_parameters：为 properties 中除 required 外的字段
4. 判断任务编排依赖关系：
   - 对每个工具标注 `execution_mode`（"sequential" or "parallel"）
   - 标明依赖关系 `depends_on`：如果参数依赖前一工具输出，请注明工具名
5. 编写任务执行说明 `task_sequence`

# 追问逻辑：
- 仅针对工具链中缺失的必选参数进行追问
- 后续工具的参数若来自前一个工具输出，则不追问
- 仅对required参数进行追问, optional 参数一律不追问
- 追问内容以自然语言形式给出
- 仅对required参数进行追问, optional 参数一律不追问

# 输出格式：
```json
{{
  "tool_chain": [
    {{
      "name": "create_vm",
      "description": "创建虚拟机",
      "parameters": {{
        "vm_name": null
      }},
      "required_parameters": [],
      "optional_parameters": ["vm_name"],
      "execution_mode": "sequential",
      "depends_on": []
    }},
    {{
      "name": "start_vm",
      "description": "启动虚拟机",
      "parameters": {{
        "vmid": null
      }},
      "required_parameters": ["vmid"],
      "optional_parameters": [],
      "execution_mode": "sequential",
      "depends_on": ["create_vm"]
    }}
  ],
  "task_sequence": "先调用 create_vm 创建虚拟机，然后使用 start_vm 启动它。",
  "follow_up": []
}}
```

# 错误处理：
若未匹配到任何工具，请输出以下 JSON 格式：
{{
  "error": "no_matching_intent",
  "message": "{tips}"
}}

#重要注意事项：
    只输出 JSON 格式，不要添加多余解释。
    若意图不清晰，推测最合理的工具，保持谨慎。

#输入信息如下：
tools: {tools}
context: {context}
user_input: {user_input}
"""
        return prompt.format(user_input=user_input, tools=tools, context=context, tips=tips, **kwargs)
