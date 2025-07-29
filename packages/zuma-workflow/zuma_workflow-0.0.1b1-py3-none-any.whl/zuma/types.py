import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ZumaExecutionStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"


class ZumaComponentType(Enum):
    WORKFLOW = "Workflow"
    PARALLEL_ACTION = "ParallelAction"
    ACTION = "Action"
    CONDITIONAL = "Conditional"


class ZumaResult(BaseModel):
    """Represents the execution result of a Zuma workflow component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    type: ZumaComponentType
    status: ZumaExecutionStatus = ZumaExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    children: List["ZumaResult"] = Field(default_factory=list)
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state (success, failed, cancelled)."""
        return self.status in {
            ZumaExecutionStatus.SUCCESS,
            ZumaExecutionStatus.FAILED,
            ZumaExecutionStatus.CANCELLED,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with improved serialization."""
        result = {
            "step_name": self.name,
            "type": self.type.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration,
        }

        if self.error:
            result["error"] = self.error
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def to_json(self, indent: int = None) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
