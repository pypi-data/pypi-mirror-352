import json
import os
import re
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Iterator,
    List,
    Optional, Union, Type,
)

import aiohttp
from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from langchain_core.pydantic_v1 import Field
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from agent.exception.custom_exception import CommonException
from agent.init_env_val import source
from agent.service.llm.custom_model import CustomModel
from agent.utils.dde_logger import dde_logger as logger
from agent.utils.http_util import async_http_post

global env_source
env_source = source

class LangchainGeoGPTDefault(LLM, CustomModel):
    def __init__(self, endpoint: str, *, streaming: bool = True, model: str = "Geogpt", system: Optional[str] = None,
                 history: Optional[list[list[str]]] = None, max_output_length: int = 3000,
                 template_name: str = "geogpt", source: str = ""):
        if history is None:
            history = []
        kwargs = {"endpoint": endpoint, " streaming": streaming, "model": model, "system": system,
                  "history": history, "max_output_length": max_output_length,
                  "template_name": template_name, "source": source}
        super().__init__(**kwargs)
        self.endpoint = endpoint
        self.streaming = streaming
        self.model = model
        self.system = system
        self.max_output_length = max_output_length
        self.template_name = template_name
        history_format = []
        for item in history:
            if item[1] is not None:
                tmp_history = {
                    "user": item[0],
                    "bot": item[1]
                }
                history_format.append(tmp_history)
        self.history = history_format
        if source != "":
            self.source = source
        else:
            global env_source
            self.source = env_source

    init_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """init kwargs for qianfan client init, such as `query_per_second` which is 
        associated with qianfan resource object to limit QPS"""

    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """extra params for model invoke using with `do`."""

    client: Any

    streaming: Optional[bool] = True
    """Whether to stream the results or not."""

    model: str
    """Model name. 
    `model` will be ignored if `endpoint` is set
    """
    is_ok: bool = False  # 是否正确返回reference
    endpoint: str
    """Endpoint of the GeoGPT LLM, required if custom model used."""

    request_timeout: Optional[int] = 60
    """request timeout for chat http requests"""
    prompt: Optional[str]
    system: Optional[str]
    history: list[list[str]]
    max_output_length: int
    template_name: str
    source: str

    top_p: Optional[float] = 0.8
    temperature: Optional[float] = 0.2
    frequency_penalty: Optional[float] = 0.0
    best_of: Optional[int] = 1
    use_beam_search: Optional[bool] = False
    presence_penalty: Optional[float] = 1.0
    top_k: Optional[int] = -1
    length_penalty: Optional[float] = 1.0

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            **{"endpoint": self.endpoint, "model": self.model},
            **super()._identifying_params,
        }

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "GeoGPT"

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling Qianfan API."""
        normal_params = {
            "system": self.system,
            "history": self.history,
            "endpoint": self.endpoint,
            "stream": self.streaming,
            "max_output_length": self.max_output_length,
            "template_name": self.template_name,
            "source": self.source
        }

        return {**normal_params, **self.model_kwargs}

    def _convert_prompt_msg_params(
            self,
            prompt: str,
            **kwargs: Any,
    ) -> dict:
        if "streaming" in kwargs:
            kwargs["stream"] = kwargs.pop("streaming")
        return {
            **{"prompt": prompt},
            **self._default_params,
            **kwargs,
        }

    async def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        """Call out to an LLM models endpoint for each generation with a prompt.
        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.
        Returns:
            The string generated by the model.
        """
        if self.streaming:
            return ""
        params = self._convert_prompt_msg_params(prompt, **kwargs)
        response_payload = await self.http_request(**params)
        return response_payload["data"]["output"]

    async def _acall(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        if self.streaming:
            stream_iter = self._astream(prompt, stop, run_manager, **kwargs)
            res = ""
            async for msg in stream_iter:
                res = msg
            return res
        return self._call(prompt, stop, run_manager, **kwargs)

    def _stream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        logger.error("检查streaming接口传了没，streaming默认为True")
        yield GenerationChunk(text="")

    async def _astream(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> AsyncIterator[GenerationChunk]:
        params = self._convert_prompt_msg_params(prompt, **{**kwargs, "stream": True})
        sseresp = self.ahttp_request_stream(**params)
        async with sseresp as r:
            if r.status != 200:
                logger.error(f"调用大模型{self.model}出错，返回为[{r}]")
                raise CommonException()
            reference_split_byte = b',"output":""}'
            pattern = "\[\[citation:(\d+)\]\]"
            pattern2 = "\[citation:(\d+)\]"
            replacement = r"<sup>[\1]</sup>"  # 前端上标标签
            async for chunk in r.content.iter_any():
                if reference_split_byte in chunk:
                    self.is_ok = True
                    index = chunk.find(reference_split_byte)
                    msg = chunk[len('{"context":'):index]
                else:
                    msg = chunk[len('{"output": "'):-3]
                result = msg.decode()
                # 替换字符串中的[[citation:*]]为<sup>[*]</sup>
                result = re.sub(pattern, replacement, result)
                result = re.sub(pattern2, replacement, result)
                print(result)
                chunk = GenerationChunk(text=result)
                yield chunk

    @staticmethod
    async def http_request(prompt, system, history, endpoint, stream, max_output_length, template_name, source):
        service_params = {
            "promptTemplateName": template_name,
            "stream": stream,
            "maxOutputLength": max_output_length
        }
        if system is not None:
            service_params.update({"system": system})
        data = {
            "input": prompt,
            "serviceParams": service_params,
            "history": history
        }
        data_log = {
            "input": prompt[:2000],
            "serviceParams": service_params,
            "history": history,
        }
        logger.info(f"调用大模型的source为: {source}, endpoint为：{endpoint},参数为：{data_log}")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        }
        # response = requests.post(endpoint, json=data, headers=headers, stream=stream)

        response = await async_http_post(url=endpoint, data=data, headers=headers)
        # response = json.loads(response)
        return response

    @staticmethod
    def ahttp_request_stream(prompt, system, history, endpoint, stream, max_output_length, template_name, source):
        service_params = {
            "promptTemplateName": template_name,
            "stream": stream,
            "maxOutputLength": max_output_length
        }
        if system is not None:
            service_params.update({"system": system})
        data = {
            "input": prompt,
            "serviceParams": service_params,
            "history": history
        }
        data_log = {
            "input": prompt[:2000],
            "serviceParams": service_params,
            "history": history,
        }
        logger.info(f"调用大模型的source为: {source}, endpoint为：{endpoint},参数为：{data_log}")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        }
        sseresp = aiohttp.request("POST", endpoint, headers=headers, data=json.dumps(data))
        return sseresp

    def with_structured_output(self, schema: Union[Dict, Type[BaseModel]], **kwargs: Any) -> Runnable[
        LanguageModelInput, Union[Dict, BaseModel]]:
        pass

    # 新大模型默认不需要system和prompt改造
    @staticmethod
    def deal_prompt(prompt: str):
        # tem_prompt = prompt.split("#System#")[-1]
        # prompt_list = tem_prompt.split("#Input#")
        return None, None


