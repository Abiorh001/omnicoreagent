from datetime import datetime
from typing import Optional
from mcpomni_connect.constants import date_time_func


class OmniAgentPromptBuilder:
    def __init__(self, system_suffix: str):
        self.system_suffix = system_suffix.strip()
        self.current_date_time = date_time_func["format_date"]()

    def build(self, *, system_instruction: str) -> str:
        if not system_instruction.strip():
            raise ValueError("System instruction is required.")

        return f"""{system_instruction.strip()}

---

{self.system_suffix}

The current date and time is: {self.current_date_time}
You do not need a tool to get the current Date and Time. Use the information available here.
""".strip()


# omniagent/prompts/react_suffix.py
