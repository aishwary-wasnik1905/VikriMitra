from abc import ABC, abstractmethod
from typing import Any


class ILLMAgent(ABC):
    """
    Common interface for all VikriMitra agents.

    Both the Groq-backed agent and the rule-based fallback
    must implement this interface.
    """

    @abstractmethod
    def process_query(self, query: str) -> dict[str, Any]:
        """
        Process a natural-language analytics query.

        Returns a structured dictionary containing the
        selected tool, parameters, and result.
        """
        raise NotImplementedError