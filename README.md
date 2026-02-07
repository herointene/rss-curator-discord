# RSS Curator

每天自动抓取精选科技/AI 文章，智能翻译摘要并推送到 Discord 频道。

---

## 👤 For Humans

### 功能特性
- **📰 多源聚合**: 自动抓取 TechCrunch, The Verge, MIT Tech Review, 机器之心等优质 RSS 源。
- **🌐 智能翻译**: 自动检测语言，调用 Google Translate API 将英文摘要翻译为中文。
- **💬 Discord 推送**: 格式化排版，支持缩略图、来源标注及原文链接。
- **⚖️ 权重优化**: (开发中) 根据用户反馈自动调整 RSS 源权重。

### 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/rss-curator.git
   cd rss-curator
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   创建 `.env` 文件或导出以下变量：
   ```bash
   # 必填：Discord Webhook 地址
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

   # 选填：Google Translate API Key (不填则跳过翻译)
   export GOOGLE_TRANSLATE_API_KEY="your-api-key"
   ```

4. **运行**
   ```bash
   python src/main.py
   ```

---

## 🤖 For Agents

如果你是一个 AI Agent (如 OpenClaw, AutoGPT 等)，请遵循以下指南来操作本项目。

### 1. 环境检查 (Healthcheck)
在执行任务前，请先验证运行环境：

- **依赖检查**:
  执行 `pip install -r requirements.txt` 确保依赖就绪。
- **环境变量**:
  检查 `DISCORD_WEBHOOK_URL` 是否存在。如果没有，请提示用户提供。
  检查 `GOOGLE_TRANSLATE_API_KEY` 是否存在。如果不存在，告知用户翻译功能将不可用。

### 2. 常用操作指令

**运行一次抓取任务:**
```bash
python src/main.py
```

**添加新的 RSS 源:**
读取 `config/sources.json`，在 `sources` 列表中添加新的对象：
```json
{
  "name": "New Source Name",
  "url": "https://example.com/feed.xml",
  "weight": 1.0,
  "lang": "en"
}
```

**调整源权重:**
直接修改 `config/sources.json` 中的 `weight` 字段 (范围 0.1 - 2.0)。

### 3. 故障排查
- 如果 `main.py` 报错 `requests.exceptions.MissingSchema`，检查 `DISCORD_WEBHOOK_URL` 格式。
- 如果日志显示 `Translation error`，通常是因为 API Key 无效或配额耗尽，脚本会自动降级使用原文。

### 4. 项目结构
- `src/main.py`: 入口文件
- `src/rss_fetcher.py`: RSS 解析逻辑
- `src/translator.py`: 翻译服务
- `src/discord_sender.py`: 消息推送
- `config/sources.json`: RSS 源配置

---
License: MIT
