import time
from typing import Dict, Any, Optional, Generator
from .llm_provider import LLMProvider

class MockProvider(LLMProvider):
    """
    Mock LLM Provider for local testing and budget saving.
    Simulates ReAct style responses based on keywords.
    """
    def __init__(self, model_name: str = "mock-model", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        time.sleep(1)  # Simulate network latency
        
        prompt_lower = prompt.lower()
        content = "Final Answer: Xin lỗi, tôi không hiểu câu hỏi của bạn. Tôi có thể giúp bạn tìm hiểu về MacBook hoặc các cửa hàng laptop tại Quận 1."

        # Mock ReAct Logic for Laptops
        if "giá" in prompt_lower or "price" in prompt_lower:
            if "macbook" in prompt_lower:
                content = "Thought: Người dùng muốn biết giá MacBook. Tôi sẽ dùng công cụ CheckPrice.\nAction: CheckPrice(macbook air m1)\nObservation: {\"item\": \"macbook air m1\", \"price\": \"18.500.000 VNĐ\"}\nFinal Answer: MacBook Air M1 hiện có giá khoảng 18.500.000 VNĐ."
            else:
                content = "Thought: Người dùng hỏi về giá nhưng chưa rõ mẫu nào. Tôi sẽ hỏi lại.\nFinal Answer: Bạn đang quan tâm đến giá của mẫu laptop cụ thể nào? (Ví dụ: MacBook Air M1, Dell XPS 13)"
        
        elif "shop" in prompt_lower or "cửa hàng" in prompt_lower:
            content = "Thought: Người dùng muốn tìm cửa hàng. Tôi cần biết vị trí.\nAction: GetUserLocation()\nObservation: Quận 1, TP. Hồ Chí Minh\nFinal Answer: Có nhiều cửa hàng tại Quận 1 như Phong Vũ, FPT Shop và CellphoneS."

        elif "hello" in prompt_lower or "chào" in prompt_lower:
            content = "Final Answer: Xin chào! Tôi là trợ lý AI chuyên về laptop. Tôi có thể giúp gì cho bạn?"

        return {
            "content": content,
            "usage": {
                "prompt_tokens": len(prompt.split()) * 2,
                "completion_tokens": len(content.split()) * 2,
                "total_tokens": (len(prompt.split()) + len(content.split())) * 2
            },
            "latency_ms": 1000,
            "provider": "mock"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        response = self.generate(prompt, system_prompt)["content"]
        for word in response.split():
            yield word + " "
            time.sleep(0.05)
