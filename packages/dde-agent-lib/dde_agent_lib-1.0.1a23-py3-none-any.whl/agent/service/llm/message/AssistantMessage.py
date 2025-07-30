from langchain_core.messages import AIMessage
from typing import Literal


class AssistantMessage(AIMessage):


    type: Literal["assistant"] = "assistant"

