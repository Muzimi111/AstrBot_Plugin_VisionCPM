import aiohttp
import json
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import ProviderRequest
import astrbot.api.message_components as Comp
from astrbot.api import logger

# ================= 配置区域 =================
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
# 确保这个名字和你在 ollama list 里看到的完全一致
MINICPM_MODEL_NAME = "minicpm-v:latest" 
# ============================================

@register("vision_cpm", "Muzimi111", "MiniCPM 视觉前置处理器", "1.0")
class VisionCPM(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def call_minicpm(self, base64_image: str) -> str:
        """调用本地 Ollama 进行图像识别"""
        payload = {
            "model": MINICPM_MODEL_NAME,
            "prompt": "请识别图中的核心物品、文字或环境特征，用 50 字以内的关键词描述。",
            "images": [base64_image],
            "stream": False
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(OLLAMA_API_URL, json=payload) as response:
                    if response.status == 200:
                        res_data = await response.json()
                        return res_data.get("response", "").strip()
                    else:
                        logger.error(f"MiniCPM 视觉调用失败，状态码: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"无法连接到 Ollama: {e}")
            return ""

    # =====================================================================
    # 核心钩子：在大模型思考前，截获请求并注入视觉信息
    # =====================================================================
    @filter.on_llm_request()
    async def pre_process_vision(self, event: AstrMessageEvent, req: ProviderRequest):
        # 1. 检查用户的原始消息链中是否包含图片
        message_chain = event.message_obj.message
        if not message_chain:
            return

        image_descriptions = []

        for comp in message_chain:
            # 找到图片组件
            if isinstance(comp, Comp.Image):
                logger.info("👀 截获图片！正在唤醒 MiniCPM 视觉皮层...")
                try:
                    # 使用底层框架提供的方法，安全提取 base64 编码
                    base64_str = await comp.convert_to_base64() 
                    
                    # 移交视觉模型处理
                    desc = await self.call_minicpm(base64_str)
                    
                    if desc:
                        logger.info(f"🧠 视觉皮层识别完成: {desc}")
                        image_descriptions.append(desc)
                        
                except Exception as e:
                    logger.error(f"图片提取或识别失败: {e}")

        # 2. 潜意识注入：如果我们成功识别到了图片内容，就把结果塞给 Qwen 的系统提示词
        if image_descriptions:
            # 将多张图片的描述合并
            all_desc = "；".join(image_descriptions)
            
            # 构建“舞台旁白”
            vision_context = (
            f"\n<vision>\n你（高木）刚才眯起眼睛看了一眼西片发来的照片，发现里面有：{all_desc}。\n</vision>\n"
            "【关键指令】：不要复述 <vision> 里的文字。请结合这些细节，用你那调皮、捉弄人的语气跟西片聊天。"
            "如果西片在显摆或者学习，记得给他一点‘意外的评价’。"
            )
            
            # 注入到请求中
            if req.system_prompt:
                # 将视觉信息置于系统提示词的最顶部，优先级最高
                req.system_prompt = vision_context + req.system_prompt
            else:
                req.system_prompt = vision_context

            logger.info("💉 视觉信息已成功注入到 Qwen 的潜意识 (System Prompt) 中！")
