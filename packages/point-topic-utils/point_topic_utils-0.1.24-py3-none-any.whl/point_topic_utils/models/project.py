from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Project:
    name: str
    current_run_status: str
    last_run_date: datetime
    logs: List[str] = field(default_factory=list)
    last_run_command: str = ""

    def to_dict(self):
        return {
            "name": self.name,
            "current_run_status": self.current_run_status,
            "last_run_date": self.last_run_date,
            "logs": self.logs,
            "last_run_command": self.last_run_command
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data) 