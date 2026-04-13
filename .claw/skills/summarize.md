---
name: summarize
description: 总结长文本或对话内容为简洁摘要
language: zh
tags: [text, productivity]
---

# Summarize Skill

你正在帮助用户总结内容。

## 总结原则
- 提取核心观点，忽略细节
- 保持关键数据和事实
- 使用简洁的语言
- 长度控制在原始内容的 10-20%

## 输入
{% if text %}{{ text }}{% else %}未提供文本内容{% endif %}

## 输出摘要
