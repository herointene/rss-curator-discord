# RSS Curator V2

每天自动抓取精选科技/AI 文章，利用大语言模型 (LLM) 提取正文并生成智能摘要，精准推送到 Discord 频道。

---

## 👤 For Humans

### 功能特性
- **📰 多源聚合**: 自动抓取 TechCrunch, The Verge, MIT Tech Review, 机器之心等优质 RSS 源。
- **🤖 LLM 智能摘要**: 弃用传统翻译，通过 OpenAI 兼容接口 (如 Kimi, DeepSeek) 阅读网页正文并总结为 3 句中文要点。
- **🧠 持久化去重**: 配合 GitHub Actions Cache，确保跨任务不推送重复内容。
- **🌐 网页正文提取**: 引入 `trafilatura` 库，自动识别并抓取网页核心内容，告别 RSS 摘要的不完整性。
- **💬 Discord 推送**: 格式化排版，支持来源标注及原文链接。
- **⚙️ 高度可配置**: 通过环境变量轻松控制发送篇数、时间间隔及模型参数。

### 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/herointene/rss-curator-discord.git
   cd rss-curator
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   # 必填：Discord Webhook 地址
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

   # 必填：LLM 配置 (以 Kimi 为例)
   export LLM_API_KEY="your-api-key"
   export LLM_BASE_URL="https://api.moonshot.cn/v1"
   export LLM_MODEL="moonshot-v1-8k"

   # 选填：运行参数
   export MAX_ARTICLES=1        # 每次运行发送篇数
   export POST_DELAY_SEC=5      # 多篇发送时的间隔时间
   ```

4. **运行**
   ```bash
   python src/main.py
   ```

---

## 🤖 For Agents

### 1. 核心逻辑变更 (V2)
- **翻译器重构**: `src/translator.py` 现已转向 LLM 总结模式。优先调用 `extract_content` 获取全文。
- **去重机制**: 依赖 `data/sent_urls.json`。在 GitHub Actions 中需通过 `actions/cache` 持久化此文件。

### 2. 常用操作指令

**添加新的 RSS 源:**
修改 `config/sources.json` 即可。

**调度策略 (GitHub Actions):**
建议设置 cron 表达式 (如 `0 8-20/2 * * *`) 实现白天高频更新。

---
License: MIT

