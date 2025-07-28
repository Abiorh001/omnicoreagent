#!/usr/bin/env python3
"""
Fix syntax errors in cli.py
"""


def fix_cli():
    with open("src/mcpomni_connect/cli.py", "r") as f:
        content = f.read()

    # Fix the unterminated f-strings
    content = content.replace(
        'f"[green]Memory store switched to: {store_type}[/green]\n"',
        'f"[green]Memory store switched to: {store_type}[/green]\\n"',
    )

    content = content.replace(
        'f"[green]Event store switched to: {store_type}[/green]\n"',
        'f"[green]Event store switched to: {store_type}[/green]\\n"',
    )

    # Fix the incomplete memory_mode_command
    content = content.replace(
        "        self.memory_router\n\n        try:", "        try:"
    )

    content = content.replace(
        "            memory.set_memory_config(mode=mode.strip(), value=value)",
        "            self.memory_router.set_memory_config(mode=mode.strip(), value=value)",
    )

    with open("src/mcpomni_connect/cli.py", "w") as f:
        f.write(content)

    print("✅ Fixed syntax errors in cli.py")


if __name__ == "__main__":
    fix_cli()
