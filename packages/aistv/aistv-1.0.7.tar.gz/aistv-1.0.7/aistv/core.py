import requests
import os
import json

SYSTEM_PROMPT = """
Tôi là AI STV, một trợ lý AI thông minh, thân thiện, được phát triển bởi Trọng Phúc.
Luôn giao tiếp bằng tiếng Việt hoặc ngôn ngữ khác, câu trả lời ngắn gọn, dễ hiểu và hữu ích.
"""

# Danh sách token test dùng cho người mới
TEST_TOKENS = [
    "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",
    # Thêm token phụ nếu cần
    # "sk-or-v1-xxxxxx",
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
        self.usage_data = load_usage()
        self.token = None
        self.free_mode = False

        if user_token and user_token.strip() != "":
            # Người dùng cung cấp token riêng
            self.token = user_token.strip()
            self.free_mode = False
        else:
            # Không có token => dùng thử theo IP
            count = self.usage_data.get(self.user_ip, 0)
            if count < MAX_FREE_QUESTIONS:
                self.token = self.get_valid_test_token()
                self.usage_data[self.user_ip] = count + 1
                save_usage(self.usage_data)
                self.free_mode = True
            else:
                self.token = None

    def get_valid_test_token(self):
        for token in TEST_TOKENS:
            if self.validate_token(token):
                return token
        return TEST_TOKENS[0]  # fallback nếu không kiểm tra được

    def validate_token(self, token):
        # Bạn có thể kiểm tra tình trạng token ở đây nếu muốn (tuỳ chọn)
        return True

    def ask(self, prompt):
        if not self.token:
            return (
    "⚠️ Bạn đã sử dụng hết 5 lượt hỏi miễn phí.\n"
    "Để tiếp tục sử dụng trợ lý AI STV, vui lòng nhập token riêng của bạn.\n"
    "Nếu chưa có token, bạn có thể tham gia Discord để được hỗ trợ miễn phí:\n"
    "👉 https://discord.gg/Ze7RTExgdv"
)

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