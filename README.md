# 👁️ MiniCPM 视觉前置处理器 (VisionCPM)

这是一个为 AstrBot 打造的“视觉皮层”插件。它利用本地部署的 **MiniCPM-V** 多模态大模型，让原本只有语言能力的 LLM（如 Qwen 2.5）能够“看见”并理解用户发送的图片。

## ✨ 核心特性

* **🧠 潜意识注入架构**: 采用 `on_llm_request` 钩子技术，在请求发送至主模型前，将图片描述注入 `system_prompt`。
* **🎨 高木式视角转换**: 自动将 MiniCPM 的客观描述转化为“高木同学的视角”进行包装，确保主模型回答不偏题，保持人格一致性。
* **🚀 零侵入处理**: 不修改原始消息链组件，仅在请求流层面进行“旁白”补充，保证聊天记录的纯净与原图显示。
* **🖇️ 多图并发支持**: 自动识别消息链中的所有 `Comp.Image` 组件，并汇总识别结果。
* **⚡ 显存自适应**: 配合 Ollama 的按需加载机制，仅在处理图片时占用显存，平时零开销。

## ⚙️ 环境依赖

* **AstrBot 框架**: v3.4.21 或更高版本（需支持 `on_llm_request` 钩子）。
* **Ollama**: 本地运行，并已下载模型：`ollama run minicpm-v`。
* **Python 库**: `aiohttp` (用于异步请求 Ollama API)。

## 🚀 快速配置

1. **模型准备**: 确保你的 Ollama 已经下载并可以运行 `minicpm-v`（或你在配置中指定的其他多模态模型）。
2. **修改配置**: 在 `main.py` 中确认你的 Ollama 地址：
   ```python
   OLLAMA_API_URL = "[http://127.0.0.1:11434/api/generate](http://127.0.0.1:11434/api/generate)"
   MINICPM_MODEL_NAME = "minicpm-v"
