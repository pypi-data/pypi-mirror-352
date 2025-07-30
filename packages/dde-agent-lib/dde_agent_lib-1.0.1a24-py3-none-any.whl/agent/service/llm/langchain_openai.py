from io import StringIO
from typing import Optional, Union, AsyncGenerator
from langchain.schema import (
    SystemMessage
)
from langchain_core.prompts import PromptTemplate
from ratelimit import limits

from agent.utils.nacos_val import get_system_config_from_nacos
from agent.init_env_val import llm_limit, source
from agent.service.llm.message.AssistantMessage import AssistantMessage
from agent.service.llm.message.UserMessage import UserMessage
from agent.service.llm.openai.my_chat_openai import MyChatOpenAI
from agent.utils.dde_logger import dde_logger as logger
from asgi_correlation_id import correlation_id

import uuid
global call_limits
global llm_call_period
try:
    system_config = get_system_config_from_nacos()
    call_limits = system_config['limits']['call_limits']
    llm_call_period = system_config['limits']['llm_call_period']
except Exception as e:
    call_limits = llm_limit
    llm_call_period = 1

class LangchainOpenai:

    def __init__(self, openai_api_base: str,  streaming: bool, model: str = "", *, openai_api_key: Optional[str] = "None",
                 system: Optional[str] = None, prompt: Optional[str] = None,
                 input_variables: list[str] = None, history: list[list[str]] = None, return_all: bool = True, **kwargs):
        '''
        openai_api_base: str,  模型服务地址
        streaming: bool  是流式调用还是非流式调用
        model: str    模型名称，例如 gpt-4
        openai_api_key: str,   模型服务apikey，没有不填
        system: Optional[str] = None   系统提示词
        prompt: Optional[str] = None,  prompt提示词，可以不填，
                    1）prompt不填，调用acall方法时，需传入完成的大模型提示词
                    例子：prompt不填，input_variables不填，acall中_input填写"回答用户问题，\n以json字段返回\n你是谁"

                    2）填prompt，占位字段要填写相应的input_variables,调用acall方法时要传入字典类型占位字段赋值
                    例子：prompt为"回答用户问题，\n{format}\n{query}"  ， input_variables为["query","format"]， acall中_input
                    值为{"query": "你是谁","format": "以json字段返回"}
        input_variables: list[str] = None,
        history=None, list[list[]] [question, answer]
        return_all: 流式调用结果返回时，返回增量还是全量， 默认为全量
        **kwargs  调用模型的其他参数，可以不传，使用字典形式传入


        举例：
        client = LangchainOpenai(url, model=model, streaming=False, prompt="回答用户问题，\n{format}\n{query}",
                                 input_variables=["query", "format"],
                                 **config)
        res = await client.acall({"query": "你是谁", "format": "以json字段返回"})
        '''
        if model is None:
            model = ""
        if "dashscope.aliyuncs.com" in openai_api_base:
            config = get_system_config_from_nacos()
            openai_api_key = config["model"]["dashscope_key"]
            model = config["model"]["dashscope_model"]
        logger.info(f"LangchainOpenai,openai_api_key:{openai_api_key},model:{model},openai_api_base:{openai_api_base}")
        client = MyChatOpenAI(streaming=streaming, openai_api_key=openai_api_key, model=model,
                              openai_api_base=openai_api_base)

        request_id = correlation_id.get()
        if not request_id:
            request_id = "req_" + str(uuid.uuid4())
        client.requestId = request_id
        if 'temperature' in kwargs:
            client.temperature = kwargs['temperature']
            del kwargs['temperature']
        if 'n' in kwargs:
            client.n = kwargs['n']
            del kwargs['n']
        self.extra_body = kwargs

        messages = []
        if system is not None:
            system_message = SystemMessage(content=system)
            messages.append(system_message)

        if history is None:
            history = []
        for item in history:
            if item[1] is not None:
                hum_msg = UserMessage(item[0])
                ass_msg = AssistantMessage(item[1])
                messages.append(hum_msg)
                messages.append(ass_msg)
        template = None
        if prompt is not None:
            template = PromptTemplate(
                template=prompt,
                input_variables=input_variables

            )
        self.messages = messages
        self.client = client
        self.template = template
        self.return_all = return_all
        self.streaming = streaming


    async def acall(self, _input: Union[str, dict]) -> AsyncGenerator[str, None] or str:
        if self.streaming:
            return self.astream(_input)
        else:
            return await self.ainvoke(_input)

    async def ainvoke(self, _input) -> str:
        self.deal_prompt(_input)
        resp = await self.client.ainvoke(self.messages, extra_body=self.extra_body)
        return resp.content

    @limits(calls=call_limits, period=llm_call_period, raise_on_limit=True)
    async def astream(self, _input) -> AsyncGenerator[str, None]:
        self.deal_prompt(_input)
        if self.return_all:
            with StringIO() as str_io:
                async for msg in self.client.astream(self.messages, extra_body=self.extra_body):
                    str_io.write(msg.content)
                    yield str_io.getvalue()
        else:
            async for msg in self.client.astream(self.messages, extra_body=self.extra_body):
                yield msg.content

    def deal_prompt(self, input):
        if self.template is not None:
            input = self.template.format(**input)
        self.messages.append(UserMessage(input))

