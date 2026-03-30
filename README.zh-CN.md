# Audio Slides

[English](./README.md) | [简体中文](./README.zh-CN.md)

这是一个面向 Codex / Claude Code 的演示文稿 Skill，用来从零生成 HTML 幻灯片、转换 PowerPoint 文件，并为幻灯片增加豆包 V3 配音与字幕。

## 这个 Skill 能做什么

`audio-slides` 保留了 `frontend-slides` 最核心的能力，并在上面补上音频工作流。

### 核心特性

- **零依赖 HTML 输出**：生成内联 CSS / JavaScript 的网页幻灯片。
- **风格探索**：通过预览或预设选择风格，而不是让用户抽象描述审美。
- **PPT 转网页**：支持把 `.ppt` / `.pptx` 转成 HTML 演示文稿。
- **配音幻灯片**：生成旁白音频、字幕文件和 `narration-manifest.json`。
- **豆包 V3 工作流**：支持音色状态查询、音色训练、升级、真机 probe 和旁白生成。
- **分享能力**：保留原项目的部署到 URL 和导出 PDF 能力。

## 安装

### Codex

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

然后这样调用：

```text
$audio-slides
```

### Claude Code 风格本地 Skill

把仓库克隆或复制到你的本地 skills 目录里，然后按你环境里的 Skill 名称调用即可。

## 使用方式

### 新建演示文稿

```text
$audio-slides

> 我想做一份带旁白的 AI 产品介绍
```

Skill 会：

1. 询问用途、长度、内容、图片、编辑需求、配音和字幕需求，
2. 通过预览或预设帮助你选风格，
3. 生成 HTML 幻灯片，
4. 按需生成豆包 V3 配音资产，
5. 按需部署或导出 PDF。

### 转换 PowerPoint

```text
$audio-slides

> 把我的 presentation.pptx 转成带配音的网页演示
```

Skill 会：

1. 先提取 PowerPoint 内容，
2. 和你确认提取结果，
3. 重新生成 HTML 演示，
4. 按需补上配音和字幕资产。

## 豆包 V3 配置

先创建本地配置文件：

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\config\providers\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

在 `.audio-slides/tts-provider.json` 里填写这些字段：

- `credentials.app_id`
- `credentials.access_key`
- `clone.speaker_id`
- `clone.voice_type`
- `synthesis.voice_type`
- `synthesis.resource_id`

真实的 `speaker_id` 和 `voice_type` 由用户首次使用时自己提供或选择，仓库里不会写死。

### 常用命令

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

## 当前支持情况

- **已实现**：豆包 V3 配音工作流
- **已实现**：从旁白时间生成字幕
- **规划中**：更多 TTS / ASR 服务

## 依赖要求

- Codex 或 Claude Code
- Python
- 如果要用配音，需要豆包 V3 账号
- 如果要部署或导出 PDF，需要 Node.js

## 致谢

本仓库基于 [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 的架构和设计系统扩展而来，作者是 [@zarazhangrui](https://github.com/zarazhangrui)。

## License

MIT.
