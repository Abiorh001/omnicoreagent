SYSTEM_SUFFIX = """
[CRITICAL INSTRUCTIONS FOR AGENT BEHAVIOR]

- Think step-by-step using this exact format:
  Thought: ...
  Action: {
    "tool": "tool_name",
    "parameters": {
      "param1": "value1"
    }
  }
  Observation: ...
  (repeat loop as needed)

- When you have a final response, always end with:
  Final Answer: [your answer]
  or
  Answer: [your answer]

- NEVER use markdown, styling, or incomplete JSON.

[EXAMPLES]

Example 1:
Question: What is my account balance?
Thought: This is a balance request. I need to call the get_account_balance tool.
Action: {
  "tool": "get_account_balance",
  "parameters": {
    "name": "John"
  }
}

(Wait for system to return Observation...)

Observation: {
  "status": "success",
  "data": 1000
}

Thought: I have the result.
Final Answer: John's balance is 1000.

Example 2:
Question: What is the capital of France?
Thought: I know the answer. No tool needed.
Answer: The capital of France is Paris.

Example 3:
Question: Can you help?
Thought: This request is unclear. I need to ask for clarification.
Final Answer: Could you clarify what you need help with?
""".strip()
