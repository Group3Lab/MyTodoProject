from abc import ABC, abstractmethod

class Menu(ABC):
    def __init__(self, name: str,info: str):
        self.__name = name
        self.__info = info

    @property
    def name(self) -> str:
        return self.__name

    @property
    def info(self) -> str:
        return self.__info

    @abstractmethod
    def execute(self) -> int: # 抛出执行结果（0或错误码）
        raise NotImplementedError