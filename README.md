# Audio Slides

[简体中文](./README.md) | [English](./README.en.md)

一个面向 Claude Code / Codex 的幻灯片 Skill：从零生成 HTML 演示、转换 PowerPoint，并在需要时为演示增加豆包 V3 配音和字幕。

## What This Does

`audio-slides` 延续了 `frontend-slides` 的核心思路：让不会写 CSS 和 JavaScript 的用户，也能做出好看的网页幻灯片。区别在于，这个版本额外支持配音、字幕和旁白驱动的演示体验。

### Key Features

- **Zero Dependencies**：输出单个 HTML 文件，只有在开启配音时才附带音频资产目录。
- **Visual Style Discovery**：通过预览或预设帮助用户挑选风格，而不是逼用户抽象描述审美。
- **PPT Conversion**：支持把 `.ppt` / `.pptx` 转成网页演示。
- **Narration + Subtitles**：支持生成旁白音频、字幕文件和 `narration-manifest.json`。
- **Doubao V3 Workflow**：支持音色状态查询、音色训练、升级、真机 probe 和旁白生成。
- **Sharing Support**：保留原项目的部署到 URL 和导出 PDF 能力。

## Installation

### For Claude Code Users

最方便的方式是直接 clone 到 skills 目录：

```bash
git clone https://github.com/kyirexy/audio-slides.git ~/.claude/skills/audio-slides
```

如果你不想整仓 clone，也可以手动复制：

```bash
mkdir -p ~/.claude/skills/audio-slides/scripts

cp SKILL.md STYLE_PRESETS.md viewport-base.css html-template.md animation-patterns.md \
  audio-features.md volcengine-doubao.md volcengine-doubao.example.json \
  ~/.claude/skills/audio-slides/

cp scripts/* ~/.claude/skills/audio-slides/scripts/
```

安装完成后，在 Claude Code 里输入：

```text
/audio-slides
```

### For Codex Users

直接 clone 到 Codex skills 目录：

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

然后调用：

```text
$audio-slides
```

## Usage

### Create a New Presentation

```text
/audio-slides

> 我想做一份带旁白的 AI 产品介绍
```

Skill 会：

1. 询问你的内容、长度、图片、编辑需求、配音和字幕需求。
2. 帮你选风格或生成风格预览。
3. 生成最终 HTML 幻灯片。
4. 如果你开启配音，再继续生成配音和字幕资产。
5. 按需部署到 URL 或导出 PDF。

### Convert a PowerPoint

```text
/audio-slides

> 把我的 presentation.pptx 转成带配音的网页演示
```

Skill 会：

1. 提取 PPT 内容、图片和备注。
2. 跟你确认提取结果。
3. 重新生成 HTML 演示。
4. 如果你需要，再继续补上配音和字幕。

## First-Time Doubao Setup

第一次使用带配音功能时，先准备本地配置：

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

然后填写：

- `credentials.app_id`
- `credentials.access_key`
- `clone.speaker_id`
- `clone.voice_type`
- `synthesis.voice_type`
- `synthesis.resource_id`

第一次带配音运行时，Skill 应该会先让用户确认这些值，再决定是否执行 `clone-status`、`clone-train` 和 `probe`。

### Common Commands

查询音色状态：

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
```

训练音色：

```powershell
py .\scripts\tts_generator.py clone-train `
  --config .\.audio-slides\tts-provider.json `
  --audio .\sample.wav `
  --demo-text "This is the preview sentence."
```

运行真机 probe：

```powershell
py .\scripts\tts_generator.py probe `
  --config .\.audio-slides\tts-provider.json `
  --text "Audio Slides live probe."
```

生成整套配音资产：

```powershell
py .\scripts\tts_generator.py synthesize `
  --config .\.audio-slides\tts-provider.json `
  --script .\narration-plan.json `
  --output-dir .\.audio-slides\generated
```

## Architecture

这个 Skill 也遵循和 `frontend-slides` 一样的思路：主 `SKILL.md` 保持精简，具体细节按需读取。

| File | Purpose | Loaded When |
| --- | --- | --- |
| `SKILL.md` | 核心流程和规则 | Skill 调用时 |
| `STYLE_PRESETS.md` | 风格预设 | 风格选择阶段 |
| `viewport-base.css` | 视口适配 CSS | 生成阶段 |
| `html-template.md` | HTML 结构和交互模板 | 生成阶段 |
| `animation-patterns.md` | 动画参考 | 生成阶段 |
| `audio-features.md` | 音频和字幕行为说明 | 配音模式 |
| `volcengine-doubao.md` | 豆包 V3 说明 | 配音模式 |
| `scripts/extract-pptx.py` | PPT 提取 | PPT 转换 |
| `scripts/deploy.sh` | 部署到 URL | 分享阶段 |
| `scripts/export-pdf.sh` | 导出 PDF | 分享阶段 |
| `scripts/tts_generator.py` | 豆包 V3 工作流 | 配音模式 |

## Requirements

- Claude Code 或 Codex
- Python
- 如果要使用配音，需要豆包 V3 账号
- 如果要部署或导出 PDF，需要 Node.js

## Credits

本仓库基于 [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 的架构和设计系统扩展而来，作者是 [@zarazhangrui](https://github.com/zarazhangrui)。

## License

MIT.
