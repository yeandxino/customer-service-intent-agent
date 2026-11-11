# 售后智能客服 Agent · Intent Classification with LLM

> 一个能把用户问题**拆成"意图 + 标准化回复"**的售后客服 Demo。
> 核心不在界面，而在于**用 Prompt 把大模型的自由文本输出约束成可编程的 JSON**。

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![flask](https://img.shields.io/badge/web-Flask-black) ![llm](https://img.shields.io/badge/LLM-DeepSeek-4B6BFB)

---

## 解决的问题

客服系统真正难的，不是"生成一句回复"，而是**让模型输出机器能用的结构**：

- 业务方要按意图分派工单（退货 / 换货 / 物流 / 其他）
- 下游系统要能直接读字段，而不是从一段话里正则提取
- 模型偶发抽风时，页面不能崩

所以这个项目做三件事：**意图分类 + 结构化输出 + 失败兜底**。

## 它是怎么工作的

```
用户消息
   │
   ▼
Flask /chat 接口
   │
   ▼
System Prompt（强制 JSON schema）
   │
   ▼
DeepSeek Chat API
   │
   ├── 成功且能解析 → {"intent": "退货", "reply": "亲，很抱歉…"}
   ├── 请求失败     → {"intent": "其他", "reply": "系统繁忙，请稍后再试。"}
   └── JSON 解析失败 → {"intent": "其他", "reply": "抱歉，我暂时无法回答…"}
```

## 关键设计

**1. 用 Prompt 锁死输出格式**

System Prompt 里给出**完整的 JSON 模板 + 一个示例**，并明确要求"不要输出任何多余的文字"。这比事后用正则从自然语言里抠字段稳定得多。

**2. 双层兜底**

- API 层：`requests` 调用包在 `try/except` 里，异常返回 `None`，接口降级为固定话术
- 解析层：`json.loads` 失败时不抛 500，而是返回兜底话术

**结果**：无论模型怎么抽风，接口永远返回可用的 `{intent, reply}`，前端不会白屏。

**3. 密钥不进代码**

`DEEPSEEK_API_KEY` 从 `.env` 读取（`python-dotenv`），`.env` 已在 `.gitignore` 中。

## 快速开始

```bash
git clone https://github.com/yeandxino/customer-service-intent-agent.git
cd customer-service-intent-agent

pip install -r requirements.txt

# 配置密钥
cp .env.example .env        # Windows: copy .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY=sk-xxxx

python app.py
```

浏览器打开 `http://127.0.0.1:5000`，输入"我手机坏了想退掉"试试。

接口示例：

```bash
curl -X POST http://127.0.0.1:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "我的快递三天没动了"}'
```

```json
{ "intent": "物流", "reply": "亲，很抱歉让您久等了～物流信息我会帮您加急核实…" }
```

## 已知局限与改进方向

- **目前是单轮**：没有上下文记忆，多轮追问会丢失前文 → 可加会话 ID + 历史消息
- **意图是硬编码的四类**：扩类别要改 Prompt → 更好的做法是把意图表抽成配置
- **`debug=True` 仅用于开发**：部署时应关掉，用 gunicorn/uwsgi
- **没有评测集**：建议构造 50 条典型问句，跑回归看意图准确率

## 技术栈

Python · Flask · DeepSeek API · Prompt Engineering · python-dotenv
