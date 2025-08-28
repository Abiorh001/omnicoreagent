from omnicoreagent.core.constants import date_time_func


class OmniAgentPromptBuilder:
    def __init__(self, system_suffix: str):
        self.system_suffix = system_suffix.strip()
        self.current_date_time = date_time_func["format_date"]()

    def build(self, *, system_instruction: str) -> str:
        if not system_instruction.strip():
            raise ValueError("System instruction is required.")

        return f"""<system_instruction>
{system_instruction.strip()}
</system_instruction>

{self.system_suffix}

<current_date_time>
{self.current_date_time}
</current_date_time>
""".strip()
