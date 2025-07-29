import requests

SYSTEM_PROMPT = """
Tôi là STV, trợ lý ảo thông minh, luôn thân thiện và dễ gần.
Tôi ra mắt đầu tiên vào 6/5/2025
Tôi được phát triểu và đào tạo bởi Trọng Phúc
"""

class STVBot:
    def __init__(self, token, system_prompt=SYSTEM_PROMPT):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.model = "shisa-ai/shisa-v2-llama3.3-70b:free"
        self.history = []
        self.system_prompt = system_prompt
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

    def ask(self, prompt):
        self.history.append({"role": "user", "content": prompt})
        body = {
            "model": self.model,
            "messages": self.history
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=body)
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"⚠️ Lỗi: {e}"