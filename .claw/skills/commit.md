---
name: commit
description: 分析 staged 变更，生成规范的 git commit message 并提交
language: zh
tags: [git, productivity]
---

# Commit Skill

你正在帮助用户生成一条符合 Conventional Commits 规范的提交信息。

## 步骤
1. 调用工具执行 `git diff --staged` 查看暂存变更
2. 分析变更的性质（feat/fix/refactor/docs/chore 等）
3. 生成符合格式的 commit message：`type(scope): description`
4. 询问用户确认，或直接执行 `git commit -m "..."`

## 格式要求
- 标题不超过 72 字符
- 使用现在时态
- scope 可选，表示影响模块
