from langchain_core.messages import HumanMessage
from typing import Literal


class UserMessage(HumanMessage):

    type: Literal["user"] = "user"

