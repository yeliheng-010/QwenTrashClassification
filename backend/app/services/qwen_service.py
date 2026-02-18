"""
通义千问大模型服务模块（通过硅基流动 API 调用）

本模块负责：
1. 从 .env 文件中加载硅基流动平台的 API Key 和 Base URL
2. 初始化 OpenAI 兼容客户端
3. 构造垃圾分类识别的 Prompt 并调用大模型
4. 解析大模型返回的 JSON 结果

安全说明：
- SILICONFLOW_API_KEY 属于付费 API 密钥，绝对不能硬编码在代码中
- 通过 python-dotenv 从 .env 文件读取，确保代码仓库中不含任何密钥
- .env 文件已通过 .gitignore 排除，不会被提交到 Git 仓库
"""

from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv
from fastapi import HTTPException

# 加载 .env 文件中的环境变量
# 确保在模块导入时环境变量已就绪
load_dotenv()

# ============================================
# 从环境变量中读取硅基流动 API 配置
# ============================================

# SILICONFLOW_API_KEY: 硅基流动平台的 API 密钥，用于认证 API 请求
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
# SILICONFLOW_BASE_URL: 硅基流动 API 的基础 URL（OpenAI 兼容格式）
SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

# 安全校验：如果未配置 API Key，直接抛出异常，防止应用以错误状态运行
if not SILICONFLOW_API_KEY:
    raise ValueError(
        "环境变量 SILICONFLOW_API_KEY 未设置！"
        "请检查 backend/.env 文件是否存在并正确配置了 SILICONFLOW_API_KEY。"
    )

# 初始化 OpenAI 兼容客户端
# 硅基流动平台提供了与 OpenAI SDK 兼容的接口，因此可以直接使用 OpenAI SDK
client = OpenAI(
    api_key=SILICONFLOW_API_KEY,
    base_url=SILICONFLOW_BASE_URL,
)

# 定义使用的模型名称
# TEXT_MODEL: 文本模式下使用的千问大模型
# VISION_MODEL: 图片模式下使用的千问视觉大模型
TEXT_MODEL = "Qwen/Qwen2.5-72B-Instruct"
VISION_MODEL = "Qwen/Qwen2-VL-72B-Instruct"

# 合法的垃圾分类类别（中国标准四分类法）
VALID_CATEGORIES = ["厨余垃圾", "可回收物", "有害垃圾", "其他垃圾"]


def classify_garbage(content: str, is_image: bool = False) -> dict:
    """
    调用通义千问大模型进行垃圾分类识别。

    :param content: 文本内容（文本模式）或 Base64 编码的图片字符串（图片模式）
    :param is_image: 是否为图片模式。True 表示 content 是 Base64 图片，False 表示纯文本
    :return: 识别结果字典，格式为：
             {
                 "result_name": "物品名称",
                 "category": "分类类别（四选一）",
                 "advice": "投放建议"
             }
    """

    # 构建系统提示词（System Prompt），指导 AI 按照指定格式返回结果
    system_prompt = f"""
    你是一个专业的垃圾分类助手。请根据用户的输入（文本描述或图片内容），识别物品名称并进行垃圾分类。
    
    必须严格遵守以下规则：
    1. 请直接返回 JSON 内容，不要包含 Markdown 的代码块标签（如 ```json），也不要返回任何解释性文字。
    2. JSON 格式必须包含三个字段：
       - "result_name": 识别出的物品名称（简短准确）。
       - "category": 垃圾分类类别，必须严格限定为以下四个之一：{', '.join(VALID_CATEGORIES)}。
       - "advice": 投放建议（简短一句话）。
    3. 如果无法识别或物品不属于垃圾（如活体动物、非实物等），"category" 字段填 "其他垃圾"，"advice" 说明原因。
    """

    # 构造消息列表，系统提示词放在第一条
    messages = [{"role": "system", "content": system_prompt}]

    # 根据输入类型选择不同的模型和消息格式
    model = TEXT_MODEL

    if is_image:
        # 图片模式：使用视觉大模型
        model = VISION_MODEL
        # 图片模式的消息格式要求包含 image_url 类型的内容块
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": content,  # content 需为 data:image/jpeg;base64,... 格式或公开 URL
                        },
                    },
                    {"type": "text", "text": "请识别图中的物品并进行垃圾分类。"},
                ],
            }
        )
    else:
        # 文本模式：直接将用户输入的文本作为消息内容
        messages.append({"role": "user", "content": content})

    try:
        # 调用大模型 API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,  # 降低随机性，使结果更加稳定和一致
            max_tokens=512,
            # 注意：不使用 response_format={"type": "json_object"}，因为视觉模型可能不支持
        )

        # 获取 AI 返回的文本内容
        result_content = response.choices[0].message.content.strip()
        print(f"DEBUG: Raw AI Response: {result_content}")  # 打印原始响应方便调试

        # 尝试解析 AI 返回的 JSON 内容
        try:
            # 使用正则表达式提取 JSON 内容
            # 优先匹配被 ```json ... ``` 代码块包裹的内容
            json_match = re.search(r"```json\s*(.*?)\s*```", result_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 如果没有代码块包裹，尝试匹配 JSON 对象的大括号
                json_match_obj = re.search(r"\{.*\}", result_content, re.DOTALL)
                if json_match_obj:
                    json_str = json_match_obj.group(0)
                else:
                    # 最后的尝试：直接将原始内容当作 JSON 解析
                    json_str = result_content

            result_json = json.loads(json_str)

            # 类型安全检查：如果 AI 返回了列表，取第一个元素
            if isinstance(result_json, list):
                if len(result_json) > 0:
                    result_json = result_json[0]
                else:
                    raise ValueError("AI 返回了一个空列表")

            if not isinstance(result_json, dict):
                raise ValueError(f"AI 返回了意外的数据类型: {type(result_json)}")

            # 验证和补全必要字段，确保返回结果格式一致
            if "category" not in result_json:
                result_json["category"] = "其他垃圾"

            # 如果分类结果不在合法类别中，默认归为"其他垃圾"
            if result_json["category"] not in VALID_CATEGORIES:
                result_json["category"] = "其他垃圾"

            # 确保包含物品名称和投放建议字段
            if "result_name" not in result_json:
                result_json["result_name"] = "未知物品"
            if "advice" not in result_json:
                result_json["advice"] = "无法识别，请按其他垃圾处理。"

            return result_json

        except (json.JSONDecodeError, ValueError) as e:
            # JSON 解析失败时，返回友好的错误提示，而非直接抛出异常
            print(f"JSON 解析/验证错误: {e}。原始内容: {result_content}")
            return {
                "result_name": "识别失败",
                "category": "其他垃圾",
                "advice": "AI 响应格式异常，请稍后重试或尝试更清晰的图片/描述。",
            }

    except Exception as e:
        # API 调用失败时，抛出 500 错误
        print(f"AI 服务调用错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 服务调用失败: {str(e)}")
