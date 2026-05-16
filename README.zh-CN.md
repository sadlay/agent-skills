# Agent Skills

中文 | [English](README.md)

这是一个个人、多平台的 skill 集合仓库。仓库以 `skills/` 作为源码事实来源，然后把这些 skills 打包成 Claude Code 和 Codex 可用的插件分发目录。

## 安装

### Claude Code

把这个仓库添加为 plugin marketplace：

```text
/plugin marketplace add sadlay/agent-skills
```

然后安装插件：

```text
/plugin install sadlay-skills@sadlay-skills-marketplace
```

本地开发时，可以添加本地 checkout 路径：

```text
/plugin marketplace add /Users/sadlay/WorkSpace/github/agent-skills
/plugin install sadlay-skills@sadlay-skills-marketplace
```

### Codex

Codex 正常使用时不需要运行下面的 `python3` 命令。请在 Codex app/plugin UI 中添加本地插件包路径或本地 marketplace 路径：

```text
plugins/codex-sadlay-skills
```

或者：

```text
.agents/plugins/marketplace.json
```

`python3` 命令只用于仓库维护者。修改 `skills/` 下的文件后，运行它们来保持生成的插件包同步：

```bash
python3 scripts/sync-plugin-skills
python3 scripts/validate-skills
```

### 手动复制

如果某个平台只支持直接加载 skill 文件夹，可以把 `skills/` 下的单个目录复制到该平台的 skill 目录。

## 仓库结构

- `skills/` - 可正式使用的 skills。每个子目录都是一个包含 `SKILL.md` 的独立 skill。
- `drafts/` - 未完成的 skill 想法，不会被安装或打包。
- `authoring/` - 用 AI 创建 skill 时使用的提示词、规范、检查表和示例。
- `plugins/sadlay-skills/` - 由 `skills/` 生成的 Claude Code 插件包。
- `plugins/codex-sadlay-skills/` - 由 `skills/` 生成的 Codex 插件包。
- `.claude-plugin/marketplace.json` - Claude Code marketplace 描述文件。
- `.agents/plugins/marketplace.json` - Codex marketplace 描述文件。
- `registry/skills.yaml` - 人工维护的 skill 索引，记录状态、分类和平台支持。
- `scripts/` - 校验、同步、安装提示和打包辅助脚本。
- `third_party/` - 可选的上游参考，例如 `agentskills/agentskills`。

## 工作流

1. 在 `skills/<skill-name>/` 中新增或更新 skill。
2. 运行 `python3 scripts/validate-skills`。
3. 运行 `python3 scripts/sync-plugin-skills`。
4. 测试生成的插件目录。
5. 一起提交源码和生成的插件 manifest。

## Skill 结构

最小结构：

```text
skills/<skill-name>/
└── SKILL.md
```

完整结构：

```text
skills/<skill-name>/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
├── scripts/
└── assets/
```

`SKILL.md` 应该保持简洁。大段文档放到 `references/`，确定性辅助脚本放到 `scripts/`，输出时会复用的资源放到 `assets/`。

## 上游参考

本项目遵循 Agent Skills 目录模型。上游规范和参考 SDK 在：

- https://agentskills.io/specification
- https://github.com/agentskills/agentskills

不要把上游文件直接铺到本项目根目录。如有需要，请放到 `third_party/agentskills`。
