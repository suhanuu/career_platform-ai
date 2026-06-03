"""
============================================
DeepSeek API 调用封装
负责: 发送请求 + 错误处理 + 腾讯云合规审查
============================================
"""
import httpx
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, SYSTEM_PROMPT

# 超时配置 (AI推理可能需要较长时间)
TIMEOUT = httpx.Timeout(30.0, read=60.0)


async def chat_with_deepseek(user_message: str, history: list = None) -> str:
    """
    调用 DeepSeek API 进行对话

    参数:
        user_message: 用户当前消息
        history: 对话历史 [{"role":"user/assistant","content":"..."}]

    返回:
        AI 回复文本
    """
    # 组装消息列表: System Prompt + 历史记录 + 当前消息
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        # 只保留最近N轮，避免Token超限
        messages.extend(history[-20:])

    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": 0.7,     # 适中的创造性
        "max_tokens": 1024,     # 单次回复最大长度
        "stream": False,        # 非流式 (后续可改true实现打字机效果)
    }

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            error_detail = response.text
            raise Exception(f"DeepSeek API返回错误 (HTTP {response.status_code}): {error_detail}")

        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        return reply.strip()
