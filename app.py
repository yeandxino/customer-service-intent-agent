from flask import Flask, request, jsonify, render_template
import requests
import json
import os   # 新增：用来读取环境变量

app = Flask(__name__)

# 从环境变量读取 API Key（安全！）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("请在 .env 文件中设置 DEEPSEEK_API_KEY")

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"


def call_ai(messages):
    """调用DeepSeek大模型，返回AI的回复内容"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.1
    }
    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data)
        result = response.json()
        # 从返回结果中提取AI的回复文本
        return result['choices'][0]['message']['content']
    except Exception as e:
        print("调用API出错：", e)          # 终端会打印详细错误
        return None                       # 返回None表示失败


@app.route('/')
def index():
    """显示聊天页面"""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """处理用户发送的消息"""
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"intent": "其他", "reply": "请说点什么吧。"})

    # 系统提示词（Prompt Engineering），强制AI按JSON格式返回
    system_prompt = """
你是一个专业的售后智能客服助手。
你的任务是分析用户的提问，并判断属于哪种意图（退货、换货、物流查询、或者普通闲聊）。

请严格按照以下JSON格式回答我，不要输出任何多余的文字：
{
    "intent": "意图分类（退货/换货/物流/其他）",
    "reply": "根据意图，生成一段得体、礼貌的标准化回复内容"
}

示例：
用户问：我手机坏了想退掉。
你输出：{"intent": "退货", "reply": "亲，很抱歉给您带来不便。退货需要保持商品完好，请您在后台申请退货，我们将安排快递上门取件。"}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    ai_response = call_ai(messages)

    if ai_response is None:
        # 如果API调用失败，返回兜底回复
        return jsonify({"intent": "其他", "reply": "系统繁忙，请稍后再试。"})

    # 尝试解析AI返回的JSON
    try:
        data = json.loads(ai_response)
        intent = data.get("intent", "其他")
        reply = data.get("reply", "我没理解您的意思，请再说一遍。")
    except:
        # 如果解析失败（AI没按格式返回），用默认回复
        intent = "其他"
        reply = "抱歉，我暂时无法回答您的问题。"

    return jsonify({"intent": intent, "reply": reply})


if __name__ == '__main__':
    app.run(debug=True)