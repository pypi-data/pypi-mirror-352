from typing import TypeVar, Generic
from dataclasses import dataclass

# Generic type for the data field
T = TypeVar('T')

@dataclass
class Signal(Generic[T]):
    """
    Represents a signal event to be sent to the AgentPaid API.
    """
    event_name: str
    agent_id: str
    customer_id: str
    data: T
