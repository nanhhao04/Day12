import re
import logging
import json
from typing import List, Dict, Any, Optional
from ..core.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class ReActAgent:
    """
    A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Adapted for production use.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])

        return f"""
        You are an intelligent assistant specialized in helping users choose and buy laptops.

        Your goal is to:
        - Understand user requirements (budget, brand, performance, screen, purpose).
        - Recommend suitable laptop options.
        - If needed, search for products and find nearby shops.
        - Prefer practical suggestions available in Vietnam market.

        When recommending:
        - Mention key specs: CPU, RAM, GPU, screen resolution, price.
        - Keep suggestions concise (2-3 options max).

        You have access to the following tools:
        {tool_descriptions}

        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(argument)
        Observation: result of the tool call.
        ... (repeat Thought/Observation if needed)
        Final Answer: your final response.

        Example:
        Thought: I need to check the price of MacBook Air M1.
        Action: CheckPrice(macbook air m1)
        Observation: {{"item": "macbook air m1", "price": "18.500.000 VNĐ"}}
        Final Answer: The MacBook Air M1 costs 18,500,000 VNĐ.
        """

    def run(self, user_input: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Executes the ReAct loop.
        Returns a dict with 'answer' and 'usage'.
        """
        current_prompt = user_input
        if history:
            history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
            current_prompt = f"Previous conversation:\n{history_str}\n\nNew Question: {user_input}"

        steps = 0
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        while steps < self.max_steps:
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            response = result["content"]
            
            # Accumulate usage
            for k in total_usage:
                total_usage[k] += result["usage"].get(k, 0)

            # Check for Final Answer
            if "Final Answer:" in response:
                answer = response.split("Final Answer:")[-1].strip()
                return {"answer": answer, "usage": total_usage}

            # Parse Action: search_google(laptop gaming)
            action_match = re.search(r"Action:\s*(\w+)\(([^)]*)\)", response)
            if action_match:
                tool_name = action_match.group(1)
                tool_args = action_match.group(2)

                observation = self._execute_tool(tool_name, tool_args)
                current_prompt += f"\n{response}\nObservation: {observation}"
            else:
                return {"answer": response, "usage": total_usage}

            steps += 1

        return {"answer": "Agent reached max steps without final answer.", "usage": total_usage}

    def _execute_tool(self, tool_name: str, tool_input: str) -> str:
        for tool in self.tools:
            if tool["name"].lower() == tool_name.lower():
                try:
                    clean_input = tool_input.strip().strip('"').strip("'") if tool_input else ""
                    if clean_input:
                        result = tool["function"](clean_input)
                    else:
                        try:
                            result = tool["function"]()
                        except TypeError:
                            result = tool["function"]("")

                    if isinstance(result, (dict, list)):
                        return json.dumps(result, ensure_ascii=False)
                    return str(result)

                except Exception as e:
                    return f"Tool error: {str(e)}"

        return f"Tool not found: {tool_name}"
