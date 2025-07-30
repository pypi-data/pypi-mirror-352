# Constants for the spanalyzer project


from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from dataclasses import dataclass


@dataclass
class TelemetryCall:
    """Represents a telemetry operation with its details."""

    func: str
    line_number: int
    args: Optional[List[Any]] = None
    keywords: Optional[Dict[str, Any]] = None

    def __dict__(self) -> Dict[str, Any]:
        """
        Convert the TelemetryCall to a dictionary.
        """

        return {
            "func": self.func,
            "line_number": self.line_number,
            "args": self.args,
            "keywords": self.keywords,
        }
