# Audio Slides

[简体中文](./README.md) | [English](./README.en.md)

一个面向 Codex / Claude Code 的幻灯片 Skill：从零生成 HTML 演示、转换 PowerPoint，并在需要时为演示增加豆包 V3 配音和字幕。

## 它能做什么

`audio-slides` 继承了 `frontend-slides` 的基础能力，并补上音频工作流。

### 核心特性

- **零依赖输出**：生成单个 HTML 幻灯片文件，必要时附带音频资产目录。
- **风格探索**：通过预览或预设选择视觉风格。
- **PPT 转网页**：把 `.ppt` / `.pptx` 转成 HTML 演示。
- **配音与字幕**：生成旁白音频、字幕文件和 `narration-manifest.json`。
- **豆包 V3 工作流**：支持音色状态查询、音色训练、升级、真机 probe 和旁白生成。
- **分享能力**：保留原项目的部署到 URL 和导出 PDF 能力。

## 安装

### Codex

直接克隆到技能目录：

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

然后调用：

```text
$audio-slides
```

### Claude Code 风格本地 Skill

如果你使用本地 skills 目录，直接把这个仓库克隆或复制进去即可。

## 使用

### 新建演示

```text
$audio-slides

> 我想做一份带旁白的 AI 产品介绍
```

Skill 会：

1. 询问内容、长度、图片、编辑需求、配音和字幕需求。
2. 帮你选择风格。
3. 生成 HTML 幻灯片。
4. 按需生成配音和字幕资产。
5. 按需部署或导出 PDF。

### 转换 PowerPoint

```text
$audio-slides

> 把我的 presentation.pptx 转成带配音的网页演示
```

Skill 会：

1. 提取 PowerPoint 内容。
2. 和你确认提取结果。
3. 重新生成 HTML 演示。
4. 按需补上配音和字幕资产。

## 豆包 V3 配置

首次使用时，先创建本地配置文件：

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

需要填写的字段：

- `credentials.app_id`
- `credentials.access_key`
- `clone.speaker_id`
- `clone.voice_type`
- `synthesis.voice_type`
- `synthesis.resource_id`

常用命令：

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
py .\scripts\tts_generator.py probe --config .\.audio-slides\tts-provider.json --text "Audio Slides live probe."
py .\scripts\tts_generator.py synthesize --config .\.audio-slides\tts-provider.json --script .\narration-plan.json --output-dir .\.audio-slides\generated
```

更多说明见 [volcengine-doubao.md](./volcengine-doubao.md)。

## 目录结构

仓库保持和原项目接近的简洁结构：

- `SKILL.md`
- `STYLE_PRESETS.md`
- `viewport-base.css`
- `html-template.md`
- `animation-patterns.md`
- `audio-features.md`
- `volcengine-doubao.md`
- `volcengine-doubao.example.json`
- `scripts/`

## 依赖要求

- Codex 或 Claude Code
- Python
- 如果要用配音，需要豆包 V3 账号
- 如果要部署或导出 PDF，需要 Node.js

## 致谢

本仓库基于 [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 的架构和设计系统扩展而来，作者是 [@zarazhangrui](https://github.com/zarazhangrui)。

## License

MIT.
