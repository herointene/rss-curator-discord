# RSS Curator

每天自动抓取 5 条科技/AI 文章，翻译摘要后推送到 Discord，根据用户反馈优化 RSS 源。

## 功能

- 📰 每天从多个 RSS 源抓取文章
- 🌐 自动翻译英文摘要
- 💬 推送到 Discord 频道
- 👍👎 根据用户反馈优化 RSS 源权重

## RSS 源

- TechCrunch
- The Verge
- MIT Technology Review
- 机器之心
- 量子位

## 技术栈

- Python 3.11+
- GitHub Actions
- Google Translate API
- Discord Webhook

## 环境变量

```bash
GOOGLE_TRANSLATE_API_KEY=xxx
DISCORD_WEBHOOK_URL=xxx
```

## License

MIT
