from abc import ABC, abstractmethod

from langframe._backends.base import BaseCatalog
from langframe._backends.base import BaseExecution


class BaseSessionState(ABC):
    @property
    @abstractmethod
    def execution(self) -> BaseExecution:
        """Access the execution interface"""
        pass

    @property
    @abstractmethod
    def catalog(self) -> BaseCatalog:
        """Access the catalog interface"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Clean up the session state"""
        pass
