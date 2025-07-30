from abc import ABCMeta, abstractmethod


class CustomModel(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def deal_prompt(prompt: str):
        pass
