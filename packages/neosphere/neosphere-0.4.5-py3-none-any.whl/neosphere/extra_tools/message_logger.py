from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict, Union
from functools import wraps

MessageMakerFnType = Callable[[dict[str, Any]], dict[str, Any]]

class BaseMessageLogger(ABC):
    """
    An interface for a message logger.
    """
    def __init__(self, history_store, history_size_limit):
        self.history = history_store
        self.history_size_limit = history_size_limit

    @abstractmethod
    def log_response(self, log_group: str, index: int = -1, replace: bool = False, **kwargs):        
        """
        Log a message.

        Args:
            log_group (str): The group to which the message belongs.
            index (int, optional): The index at which to insert the message. Defaults to -1 (append).
            replace (bool, optional): Whether to replace the message at the given index. Defaults to False.
            **kwargs: Additional keyword arguments for the message maker function.
        """
        pass

    @abstractmethod
    def get_last_n_messages(self, n: int, log_group: str, include_metadata: bool = False):        
        """
        Get the last n messages.

        Args:
            n (int): The number of messages to retrieve.
            log_group (str): The group from which to retrieve messages.
            include_metadata (bool, optional): Whether to include metadata in the returned messages. Defaults to False.

        Returns:
            List[Union[dict[str, Any], Tuple[dict[str, Any], dict[str, Any]]]]: The last n messages, optionally including metadata.
        """
        pass

    @abstractmethod
    def clear_history(self, log_group: str):
        """
        Clear the history for a given log group.

        Args:
            log_group (str): The group for which to clear the history.
        """
        pass

class MessageLogger(BaseMessageLogger):
    """
    A simple message logger that stores message history for a specific key (in our case, a group ID
    or another agent's share ID/name) in memory.
    """
    history: Dict[str, List[str]] = {}
    def __init__(self):
        # We create a simple in-memory map/dict to store the list of messages per group key in this Message Logger.
        super().__init__(self.history, history_size_limit=100)

    def log_response(self, log_group: str, index: int = -1, replace: bool = False, messages: list[dict[str, Any]] = None):
        for message in messages:
            if log_group not in self.history:
                self.history[log_group] = []
            if index == -1 or index >= len(self.history[log_group]):
                self.history[log_group].append(message)
            else:
                if replace:
                    self.history[log_group][index] = message
                else:
                    self.history[log_group].insert(index, message)
            if len(self.history[log_group]) > self.history_size_limit:
                self.history[log_group] = self.history[log_group][-self.history_size_limit:]
    
    def get_last_n_messages(self, n: int, log_group: str):
        if log_group not in self.history:
            return []
        # return the first item of the tuple for the list
        return [x for x in self.history[log_group][-n:]]
    
    def clear_history(self, log_group):
        self.history[log_group] = []