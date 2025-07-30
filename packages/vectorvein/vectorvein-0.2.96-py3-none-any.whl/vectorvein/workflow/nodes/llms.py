from typing import Optional

from ..graph.node import Node
from ..graph.port import PortType, InputPort, OutputPort


class AliyunQwen(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="AliyunQwen",
            category="llms",
            task_name="llms.aliyun_qwen",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXT,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="qwen2.5-72b-instruct",
                    options=[
                        {"value": "qwen2.5-72b-instruct", "label": "qwen2.5-72b-instruct"},
                        {"value": "qwen2.5-32b-instruct", "label": "qwen2.5-32b-instruct"},
                        {"value": "qwen2.5-coder-32b-instruct", "label": "qwen2.5-coder-32b-instruct"},
                        {"value": "qwq-32b-preview", "label": "qwq-32b-preview"},
                        {"value": "qwen2.5-14b-instruct", "label": "qwen2.5-14b-instruct"},
                        {"value": "qwen2.5-7b-instruct", "label": "qwen2.5-7b-instruct"},
                        {"value": "qwen2.5-coder-7b-instruct", "label": "qwen2.5-coder-7b-instruct"},
                    ],
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class Baichuan(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="Baichuan",
            category="llms",
            task_name="llms.baichuan",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="Baichuan3-Turbo",
                    options=[
                        {"value": "Baichuan4", "label": "Baichuan4"},
                        {"value": "Baichuan3-Turbo", "label": "Baichuan3-Turbo"},
                        {"value": "Baichuan3-Turbo-128k", "label": "Baichuan3-Turbo-128k"},
                        {"value": "Baichuan2-Turbo", "label": "Baichuan2-Turbo"},
                        {"value": "Baichuan2-53B", "label": "Baichuan2-53B"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class BaiduWenxin(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="BaiduWenxin",
            category="llms",
            task_name="llms.baidu_wenxin",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="ernie-3.5",
                    options=[
                        {"value": "ernie-lite", "label": "ernie-lite"},
                        {"value": "ernie-speed", "label": "ernie-speed"},
                        {"value": "ernie-3.5", "label": "ernie-3.5"},
                        {"value": "ernie-4.0", "label": "ernie-4.0"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "output": OutputPort(),
            },
        )


class ChatGLM(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="ChatGLM",
            category="llms",
            task_name="llms.chat_glm",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="glm-4-air",
                    options=[
                        {"value": "glm-4-plus", "label": "glm-4-plus"},
                        {"value": "glm-4", "label": "glm-4"},
                        {"value": "glm-4-0520", "label": "glm-4-0520"},
                        {"value": "glm-4-air", "label": "glm-4-air"},
                        {"value": "glm-4-airx", "label": "glm-4-airx"},
                        {"value": "glm-4-flash", "label": "glm-4-flash"},
                        {"value": "glm-4-long", "label": "glm-4-long"},
                        {"value": "glm-zero-preview", "label": "glm-zero-preview"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class Claude(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="Claude",
            category="llms",
            task_name="llms.claude",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="claude-3-5-haiku",
                    options=[
                        {"value": "claude-3-7-sonnet-thinking", "label": "claude-3-7-sonnet-thinking"},
                        {"value": "claude-3-7-sonnet", "label": "claude-3-7-sonnet"},
                        {"value": "claude-3-5-sonnet", "label": "claude-3-5-sonnet"},
                        {"value": "claude-3-5-haiku", "label": "claude-3-5-haiku"},
                        {"value": "claude-3-opus", "label": "claude-3-opus"},
                        {"value": "claude-3-sonnet", "label": "claude-3-sonnet"},
                        {"value": "claude-3-haiku", "label": "claude-3-haiku"},
                    ],
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "output": OutputPort(),
            },
        )


class Deepseek(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="Deepseek",
            category="llms",
            task_name="llms.deepseek",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="deepseek-chat",
                    options=[
                        {"value": "deepseek-chat", "label": "deepseek-chat"},
                        {"value": "deepseek-reasoner", "label": "deepseek-r1"},
                        {"value": "deepseek-r1-distill-qwen-32b", "label": "deepseek-r1-distill-qwen-32b"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "reasoning_content": OutputPort(
                    name="reasoning_content",
                    condition="return fieldsData.llm_model.value === 'deepseek-reasoner'",
                    condition_python=lambda ports: ports["llm_model"].value == "deepseek-reasoner",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class Gemini(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="Gemini",
            category="llms",
            task_name="llms.gemini",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="gemini-1.5-flash",
                    options=[
                        {"value": "gemini-1.5-flash", "label": "gemini-1.5-flash"},
                        {"value": "gemini-1.5-pro", "label": "gemini-1.5-pro"},
                        {"value": "gemini-2.0-flash", "label": "gemini-2.0-flash"},
                        {
                            "value": "gemini-2.0-flash-thinking-exp-01-21",
                            "label": "gemini-2.0-flash-thinking-exp-01-21",
                        },
                        {"value": "gemini-2.0-pro-exp-02-05", "label": "gemini-2.0-pro-exp-02-05"},
                        {
                            "value": "gemini-2.0-flash-lite-preview-02-05",
                            "label": "gemini-2.0-flash-lite-preview-02-05",
                        },
                        {"value": "gemini-exp-1206", "label": "gemini-exp-1206"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class LingYiWanWu(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="LingYiWanWu",
            category="llms",
            task_name="llms.ling_yi_wan_wu",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="yi-lightning",
                    options=[
                        {
                            "value": "yi-lightning",
                            "label": "yi-lightning",
                        },
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "output": OutputPort(),
            },
        )


class MiniMax(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="MiniMax",
            category="llms",
            task_name="llms.mini_max",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="MiniMax-Text-01",
                    options=[
                        {"value": "abab6.5s-chat", "label": "abab6.5s-chat"},
                        {"value": "MiniMax-Text-01", "label": "MiniMax-Text-01"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class Moonshot(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="Moonshot",
            category="llms",
            task_name="llms.moonshot",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="moonshot-v1-8k",
                    options=[
                        {"value": "moonshot-v1-8k", "label": "moonshot-v1-8k"},
                        {"value": "moonshot-v1-32k", "label": "moonshot-v1-32k"},
                        {"value": "moonshot-v1-128k", "label": "moonshot-v1-128k"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class OpenAI(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="OpenAI",
            category="llms",
            task_name="llms.open_ai",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="gpt-4o-mini",
                    options=[
                        {"value": "gpt-3.5", "label": "gpt-3.5-turbo"},
                        {"value": "gpt-4", "label": "gpt-4-turbo"},
                        {"value": "gpt-4o", "label": "gpt-4o"},
                        {"value": "gpt-4o-mini", "label": "gpt-4o-mini"},
                        {"value": "o1-mini", "label": "o1-mini"},
                        {"value": "o1-preview", "label": "o1-preview"},
                        {"value": "o3-mini", "label": "o3-mini"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class XAi(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="XAi",
            category="llms",
            task_name="llms.x_ai",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="grok-beta",
                    options=[
                        {"value": "grok-beta", "label": "grok-beta"},
                    ],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )


class CustomModel(Node):
    def __init__(self, id: Optional[str] = None):
        super().__init__(
            node_type="CustomModel",
            category="llms",
            task_name="llms.custom_model",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "model_family": InputPort(
                    name="model_family",
                    port_type=PortType.SELECT,
                    value="",
                    options=[],
                ),
                "llm_model": InputPort(
                    name="llm_model",
                    port_type=PortType.SELECT,
                    value="",
                    options=[],
                ),
                "temperature": InputPort(
                    name="temperature",
                    port_type=PortType.TEMPERATURE,
                    value=0.7,
                ),
                "top_p": InputPort(
                    name="top_p",
                    port_type=PortType.NUMBER,
                    value=0.95,
                ),
                "stream": InputPort(
                    name="stream",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "system_prompt": InputPort(
                    name="system_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "response_format": InputPort(
                    name="response_format",
                    port_type=PortType.SELECT,
                    value="text",
                    options=[
                        {"value": "text", "label": "Text"},
                        {"value": "json_object", "label": "JSON"},
                    ],
                ),
                "use_function_call": InputPort(
                    name="use_function_call",
                    port_type=PortType.CHECKBOX,
                    value=False,
                ),
                "functions": InputPort(
                    name="functions",
                    port_type=PortType.SELECT,
                    value=[],
                ),
                "function_call_mode": InputPort(
                    name="function_call_mode",
                    port_type=PortType.SELECT,
                    value="auto",
                    options=[
                        {"value": "auto", "label": "auto"},
                        {"value": "none", "label": "none"},
                    ],
                ),
                "output": OutputPort(
                    name="output",
                ),
                "function_call_output": OutputPort(
                    name="function_call_output",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
                "function_call_arguments": OutputPort(
                    name="function_call_arguments",
                    condition="return fieldsData.use_function_call.value",
                    condition_python=lambda ports: ports["use_function_call"].value,
                ),
            },
        )
