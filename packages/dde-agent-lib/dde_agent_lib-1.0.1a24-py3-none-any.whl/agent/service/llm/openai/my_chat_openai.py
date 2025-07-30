from __future__ import annotations

import os
import threading
from typing import (
    Dict,
)

import openai
from agent.utils.nacos_val import get_system_config_from_nacos
from langchain_core.pydantic_v1 import root_validator
from langchain_core.utils import (
    convert_to_secret_str,
    get_from_dict_or_env,
)
from langchain_openai import ChatOpenAI


class MyChatOpenAI(ChatOpenAI):
    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        if values["n"] < 1:
            raise ValueError("n must be at least 1.")
        if values["n"] > 1 and values["streaming"]:
            raise ValueError("n must be 1 when streaming.")

        values["openai_api_key"] = convert_to_secret_str(
            get_from_dict_or_env(values, "openai_api_key", "OPENAI_API_KEY")
        )
        # Check OPENAI_ORGANIZATION for backwards compatibility.
        values["openai_organization"] = (
            values["openai_organization"]
            or os.getenv("OPENAI_ORG_ID")
            or os.getenv("OPENAI_ORGANIZATION")
        )
        values["openai_api_base"] = values["openai_api_base"] or os.getenv(
            "OPENAI_API_BASE"
        )
        values["openai_proxy"] = get_from_dict_or_env(
            values,
            "openai_proxy",
            "OPENAI_PROXY",
            default="",
        )

        client_params = {
            "api_key": (
                values["openai_api_key"].get_secret_value()
                if values["openai_api_key"]
                else None
            ),
            "organization": values["openai_organization"],
            "base_url": values["openai_api_base"],
            "timeout": values["request_timeout"],
            "max_retries": values["max_retries"],
            "default_headers": values["default_headers"],
            "default_query": values["default_query"],
            "http_client": values["http_client"],
        }

        if not values.get("client"):
            values["client"] = openai.OpenAI(**client_params).chat.completions
        if not values.get("async_client"):
            values["async_client"] = openai.AsyncOpenAI(
                **client_params
            ).chat.completions
        config = get_system_config_from_nacos()

        def check_get_remote_list(model_name: str):
            if model_name == "deepseek-r1" or model_name=="deepseek-v3":
                return False
            model_name = model_name.strip().lower()
            list = config["model"]["get_remote_list"]
            for item in list:
                if item in model_name:
                    return True
            return False

        if values["model_name"] != "" and check_get_remote_list(values.get("model_name")):
            def get_model():
                myclient = openai.Client(**client_params)
                models = myclient.models.list()
                values["model_name"] = models.data[0].id

            x = threading.Thread(target=get_model)
            x.start()
            x.join()
        return values
