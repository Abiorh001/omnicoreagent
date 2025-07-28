#!/usr/bin/env python3
"""
Update CLI to remove legacy memory commands and use new memory_router system
"""


def update_cli():
    with open("src/mcpomni_connect/cli.py", "r") as f:
        content = f.read()

    # 1. Remove MEMORY from CommandType enum
    content = content.replace('    MEMORY = "memory"', "")

    # 2. Remove old memory command help and add new memory_store and event_store
    old_memory_help = """            "memory": {
                "description": "Toggle memory usage between Redis and In-Memory",
                "usage": "/memory",
                "examples": [
                    "/memory  # Toggle memory usage between Redis and In-Memory"
                ],
                "subcommands": {},
                "tips": ["Use to toggle memory usage between Redis and In-Memory"],
            },"""

    new_memory_help = """            "memory_store": {
                "description": "Switch between different memory store backends",
                "usage": "/memory_store:<backend>[:<database_url>]",
                "examples": [
                    "/memory_store:in_memory  # Use in-memory storage",
                    "/memory_store:redis  # Use Redis storage",
                    "/memory_store:database  # Use database storage (defaults to SQLite)",
                    "/memory_store:database:postgresql://user:pass@localhost/db  # Use PostgreSQL",
                ],
                "subcommands": {
                    "in_memory": {
                        "description": "Fast in-memory storage (default)",
                        "usage": "/memory_store:in_memory",
                        "examples": ["/memory_store:in_memory"],
                        "tips": ["Best for development and testing"],
                    },
                    "redis": {
                        "description": "Redis-based persistent storage",
                        "usage": "/memory_store:redis",
                        "examples": ["/memory_store:redis"],
                        "tips": ["Requires Redis server running"],
                    },
                    "database": {
                        "description": "Database-based persistent storage",
                        "usage": "/memory_store:database[:<database_url>]",
                        "examples": [
                            "/memory_store:database  # Use SQLite (default)",
                            "/memory_store:database:postgresql://user:pass@localhost/db",
                        ],
                        "tips": ["Uses SQLite by default if no URL provided"],
                    },
                },
                "tips": [
                    "Choose based on your persistence and performance needs",
                    "Database backend supports PostgreSQL, MySQL, SQLite",
                    "Redis provides fast in-memory persistence",
                    "In-memory is fastest but loses data on restart",
                ],
            },
            "event_store": {
                "description": "Switch between different event store backends",
                "usage": "/event_store:<backend>",
                "examples": [
                    "/event_store:in_memory  # Use in-memory event storage",
                    "/event_store:redis_stream  # Use Redis Streams",
                ],
                "subcommands": {
                    "in_memory": {
                        "description": "Fast in-memory event storage (default)",
                        "usage": "/event_store:in_memory",
                        "examples": ["/event_store:in_memory"],
                        "tips": ["Best for development and testing"],
                    },
                    "redis_stream": {
                        "description": "Redis Streams for persistent event storage",
                        "usage": "/event_store:redis_stream",
                        "examples": ["/event_store:redis_stream"],
                        "tips": ["Requires Redis server running"],
                    },
                },
                "tips": [
                    "Event stores handle real-time event streaming",
                    "Redis Streams provide persistent event storage",
                    "In-memory is fastest but loses events on restart",
                ],
            },"""

    content = content.replace(old_memory_help, new_memory_help)

    # 3. Remove old memory command parsing
    content = content.replace(
        '        elif input_text == "/memory":\n            return CommandType.MEMORY, ""',
        "",
    )

    # 4. Remove old memory command handler
    old_memory_handler = '''    async def handle_memory_command(self, input_text: str = ""):
        """Handle memory command"""
        self.USE_MEMORY["redis"] = not self.USE_MEMORY["redis"]
        self.console.print(
            f"[{'green' if self.USE_MEMORY['redis'] else 'red'}]Redis memory "
            f"{'enabled' if self.USE_MEMORY['redis'] else 'disabled'}[/]"
        )

    '''
    content = content.replace(old_memory_handler, "")

    # 5. Update history command to use memory_router
    old_history = '''    async def handle_history_command(self, input_text: str = ""):
        """Handle history command"""
        prompts_table = Table(title="Message History", box=box.ROUNDED)
        prompts_table.add_column("Role", style="cyan", no_wrap=False)
        prompts_table.add_column("Content", style="green")
        if self.USE_MEMORY["redis"]:
            messages = await self.redis_short_term_memory.get_messages()
        else:
            messages = await self.in_memory_short_term_memory.get_all_messages()
            prompts_table = Table(title="Message History")
            prompts_table.add_column("Agent", style="cyan", no_wrap=True)
            prompts_table.add_column("Role", style="magenta")
            prompts_table.add_column("Content", style="white")

            for agent_name, agent_messages in messages.items():
                for message in agent_messages:
                    role = message.get("role", "unknown")
                    content = message.get("content", "")
                    prompts_table.add_row(agent_name, role, content)
        self.console.print(prompts_table)'''

    new_history = '''    async def handle_history_command(self, input_text: str = ""):
        """Handle history command"""
        prompts_table = Table(title="Message History", box=box.ROUNDED)
        prompts_table.add_column("Agent", style="cyan", no_wrap=True)
        prompts_table.add_column("Role", style="magenta")
        prompts_table.add_column("Content", style="white")
        
        messages = await self.memory_router.get_messages()
        
        if messages:
            for agent_name, agent_messages in messages.items():
                for message in agent_messages:
                    role = message.get("role", "unknown")
                    content = message.get("content", "")
                    prompts_table.add_row(agent_name, role, content)
        else:
            prompts_table.add_row("No messages", "N/A", "No history available")
            
        self.console.print(prompts_table)'''

    content = content.replace(old_history, new_history)

    # 6. Update clear history command to use memory_router
    old_clear_history = '''    async def handle_clear_history_command(self, input_text: str = ""):
        """Handle clear history command"""
        if self.USE_MEMORY["redis"]:
            await self.redis_short_term_memory.clear_memory()
        else:
            await self.in_memory_short_term_memory.clear_memory()
        self.console.print("[green]Message history cleared[/]")'''

    new_clear_history = '''    async def handle_clear_history_command(self, input_text: str = ""):
        """Handle clear history command"""
        await self.memory_router.clear_memory()
        self.console.print("[green]Message history cleared[/]")'''

    content = content.replace(old_clear_history, new_clear_history)

    # 7. Update save history command to use memory_router
    old_save_history = '''    async def handle_save_history_command(self, input_text: str):
        """Handle save history command"""
        if self.USE_MEMORY["redis"]:
            await self.redis_short_term_memory.save_message_history_to_file(input_text)
        else:
            await self.in_memory_short_term_memory.save_message_history_to_file(
                input_text
            )
        self.console.print(f"[green]Message history saved to {input_text}[/]")'''

    new_save_history = '''    async def handle_save_history_command(self, input_text: str):
        """Handle save history command"""
        await self.memory_router.save_message_history_to_file(input_text)
        self.console.print(f"[green]Message history saved to {input_text}[/]")'''

    content = content.replace(old_save_history, new_save_history)

    # 8. Update load history command to use memory_router
    old_load_history = '''    async def handle_load_history_command(self, input_text: str):
        """Handle load history command for in memory short term memory"""
        await self.in_memory_short_term_memory.load_message_history_from_file(
            input_text
        )
        self.console.print(f"[green]Message history loaded from {input_text}[/]")'''

    new_load_history = '''    async def handle_load_history_command(self, input_text: str):
        """Handle load history command"""
        await self.memory_router.load_message_history_from_file(input_text)
        self.console.print(f"[green]Message history loaded from {input_text}[/]")'''

    content = content.replace(old_load_history, new_load_history)

    # 9. Remove MEMORY from handlers mapping
    content = content.replace(
        "            CommandType.MEMORY: self.handle_memory_command,", ""
    )

    # 10. Update all memory references in handle_query to use memory_router
    content = content.replace(
        'add_message_to_history=(\n                        self.redis_short_term_memory.store_message\n                        if self.USE_MEMORY["redis"]\n                        else self.in_memory_short_term_memory.store_message\n                    )',
        "add_message_to_history=self.memory_router.store_message",
    )

    content = content.replace(
        'message_history=(\n                        self.redis_short_term_memory.get_messages\n                        if self.USE_MEMORY["redis"]\n                        else self.in_memory_short_term_memory.get_messages\n                    )',
        "message_history=self.memory_router.get_messages",
    )

    # 11. Update episodic memory command to use memory_router
    old_episodic = '''    async def handle_episodic_memory_command(self):
        """Handle episodic memory command"""
        messages = await self.in_memory_short_term_memory.get_messages()
        if messages:
            # created_episodic_memory = await self.episodic_memory.create_episodic_memory(
            #     messages=messages, llm_connection=self.llm_connection
            # )
            # TODO: add episodic memory
            created_episodic_memory = None
            self.console.print(
                f"[green]Episodic memory created: {created_episodic_memory}[/]"
            )
        else:
            self.console.print("[yellow]No messages to create episodic memory[/]")'''

    new_episodic = '''    async def handle_episodic_memory_command(self):
        """Handle episodic memory command"""
        messages = await self.memory_router.get_messages()
        if messages:
            # created_episodic_memory = await self.episodic_memory.create_episodic_memory(
            #     messages=messages, llm_connection=self.llm_connection
            # )
            # TODO: add episodic memory
            created_episodic_memory = None
            self.console.print(
                f"[green]Episodic memory created: {created_episodic_memory}[/]"
            )
        else:
            self.console.print("[yellow]No messages to create episodic memory[/]")'''

    content = content.replace(old_episodic, new_episodic)

    # 12. Update welcome header to remove old memory command
    old_memory_cmd = """            (
                "/memory",
                "Toggle memory usage between Redis and In-Memory 💾",
                "",
            ),"""
    content = content.replace(old_memory_cmd, "")

    # Add new memory commands to welcome header
    new_memory_cmds = """            (
                "/memory_store:<type>",
                "Switch memory store backend 💾",
                "/memory_store:in_memory, /memory_store:redis, /memory_store:database",
            ),
            (
                "/event_store:<type>",
                "Switch event store backend 📡",
                "/event_store:in_memory, /event_store:redis_stream",
            ),"""

    # Find the right place to insert new commands
    content = content.replace(
        '            ("/mode:<type>",',
        f'{new_memory_cmds}\n            ("/mode:<type>",',
    )

    with open("src/mcpomni_connect/cli.py", "w") as f:
        f.write(content)

    print(
        "✅ Successfully updated CLI to remove legacy memory commands and use new memory_router system"
    )


if __name__ == "__main__":
    update_cli()
