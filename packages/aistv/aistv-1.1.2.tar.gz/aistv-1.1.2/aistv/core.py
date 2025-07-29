import requests
import os
import json

SYSTEM_PROMPT = """
Tôi là AI STV,được phát triển bởi Trọng Phúc.
"""

# Danh sách token test dùng cho người mới
TEST_TOKENS = [
    "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",
    "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"
]

# Cấu hình
USAGE_LOG = "ip_usage.json"
MAX_FREE_QUESTIONS = 5

def get_user_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()["ip"]
    except:
        return "unknown"

def load_usage():
    if os.path.exists(USAGE_LOG):
        with open(USAGE_LOG, "r") as f:
            return json.load(f)
    return {}

def save_usage(data):
    with open(USAGE_LOG, "w") as f:
        json.dump(data, f)

class STVBot:
    def __init__(self, user_token=None, system_prompt=SYSTEM_PROMPT):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.system_prompt = system_prompt
        self.model = "nousresearch/deephermes-3-mistral-24b-preview:free"
        self.history = []
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

        self.user_ip = get_user_ip()
        self.token = user_token.strip() if user_token and user_token.strip() != "" else None
        self.free_mode = self.token is None
        self.usage_data = load_usage()

        if self.free_mode:
            # nếu chưa có IP trong usage_data thì khởi tạo 0
            if self.user_ip not in self.usage_data:
                self.usage_data[self.user_ip] = 0

    def get_valid_test_token(self):
        for token in TEST_TOKENS:
            if self.validate_token(token):
                return token
        return TEST_TOKENS[0]

    def validate_token(self, token):
        # Có thể thêm kiểm tra token ở đây
        return True

    def ask(self, prompt):
        # Nếu dùng free mode thì kiểm tra lượt hỏi
        if self.free_mode:
            count = self.usage_data.get(self.user_ip, 0)
            if count >= MAX_FREE_QUESTIONS:
                return (
                    "⚠️ You have used up your 5 free questions.\n"
                    "To continue using the AI assistant STV, please enter your own token.\n"
                    "If you don't have a token yet, you can join our Discord for free support:\n"
                    "👉 https://discord.gg/Ze7RTExgdv"
                )
            # cấp token test
            self.token = self.get_valid_test_token()
            # tăng lượt hỏi
            self.usage_data[self.user_ip] = count + 1
            save_usage(self.usage_data)

        self.history.append({"role": "user", "content": prompt})
        body = {
            "model": self.model,
            "messages": self.history,
            "max_tokens": 300,
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "STV Chat"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=body, timeout=15)
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            self.history.append({"role": "assistant", "content": reply})
            return reply.strip()
        except Exception as e:
            return f"⚠️ Lỗi khi kết nối API: {e}"