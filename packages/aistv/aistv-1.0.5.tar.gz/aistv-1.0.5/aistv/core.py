import requests

SYSTEM_PROMPT = """
Tôi là AI STV, một trợ lý AI thông minh, thân thiện, được phát triển bởi Trọng Phúc.
Luôn giao tiếp bằng tiếng Việt hoặc ngôn ngữ khác, câu trả lời ngắn gọn, dễ hiểu và hữu ích.
"""

class STVBot:
    def __init__(self, token, system_prompt=SYSTEM_PROMPT):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai",  # một số model cần
            "X-Title": "STV Chat"
        }
        self.model = "nousresearch/deephermes-3-mistral-24b-preview:free"
        self.history = []
        self.system_prompt = system_prompt
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

    def ask(self, prompt):
        self.history.append({"role": "user", "content": prompt})
        body = {
            "model": self.model,
            "messages": self.history,
            "max_tokens": 300,  # giới hạn độ dài trả lời
            "temperature": 0.7,  # giảm "sáng tạo" để bớt bậy bạ
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=body, timeout=15)
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            return reply.strip()
        except Exception as e:
            return f"⚠️ Lỗi: {e}"