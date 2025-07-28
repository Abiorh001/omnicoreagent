#!/usr/bin/env python3
"""
Final fixes for CLI - remove legacy MEMORY command and add new commands to welcome header
"""


def fix_cli_final():
    with open("src/mcpomni_connect/cli.py", "r") as f:
        content = f.read()

    # 1. Remove legacy MEMORY command type
    content = content.replace('    MEMORY = "memory"', "")

    # 2. Add new commands to welcome header
    old_commands_start = '        commands = [\n            (\n                "/memory_mode[:<mode>[:<value>]]",'
    new_commands_start = """        commands = [
            (
                "/memory_store:<type>[:<database_url>]",
                "Switch memory store backend 💾",
                "/memory_store:in_memory, /memory_store:redis, /memory_store:database",
            ),
            (
                "/event_store:<type>",
                "Switch event store backend 📡",
                "/event_store:in_memory, /event_store:redis_stream",
            ),
            (
                "/memory_mode[:<mode>[:<value>]]","""

    content = content.replace(old_commands_start, new_commands_start)

    with open("src/mcpomni_connect/cli.py", "w") as f:
        f.write(content)

    print(
        "✅ Successfully removed legacy MEMORY command and added new commands to welcome header"
    )


if __name__ == "__main__":
    fix_cli_final()
