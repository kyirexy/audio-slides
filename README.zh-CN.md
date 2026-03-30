# Audio Slides

[简体中文](./README.zh-CN.md) | [English](./README.md)

[![MIT License](https://img.shields.io/badge/license-MIT-0f172a.svg)](./LICENSE)
[![Skill](https://img.shields.io/badge/skill-Codex%20%2F%20Claude%20Code-2563eb.svg)](./SKILL.md)
[![Provider](https://img.shields.io/badge/provider-Doubao%20V3-16a34a.svg)](./references/volcengine-doubao.md)
[![Output](https://img.shields.io/badge/output-HTML%20Slides-f59e0b.svg)](./html-template.md)

`audio-slides` 是一个面向 Codex 或 Claude Code 的演示文稿 Skill。它完整继承了 `frontend-slides` 的核心能力，并在此基础上增加了配音、字幕、音频同步播放、豆包 V3 音色复刻工作流。

> 目标很明确：原项目能做的事情，这个仓库不能少；原项目没有的音频能力，这个仓库要补上。

## 能力覆盖

这个仓库的定位是“比 `frontend-slides` 更强”，而不是“做一个音频分支砍掉原能力”。

### 已继承的原始能力

- 从零生成 HTML 幻灯片
- 将 PPT / PPTX 转成网页幻灯片
- 增强现有 HTML 幻灯片
- 风格预览与风格预设选择
- 严格的视口适配规则
- 内联编辑能力指引
- 一键部署到 URL
- 一键导出 PDF

### 新增能力

- 豆包 V3 音色复刻配置
- 真机 probe 命令
- 旁白清单 `narration-manifest.json`
- 从合成时间生成 `.srt` / `.vtt`
- 带字幕和播放器控制区的 HTML 模板
- 音频驱动翻页与同步的设计规范

## 安装

### Codex

将仓库克隆到 Codex 的技能目录：

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

然后直接调用：

```text
$audio-slides
```

### Claude Code

如果你使用的是 Claude Code 风格的本地 Skill 目录，也可以把仓库克隆或复制到对应目录，然后用你环境里对应的 Skill 名称调用。

## 快速开始

### 纯视觉模式

1. 调用 `$audio-slides`
2. 选择新建演示、PPT 转换，或增强已有演示
3. 选择风格探索或直接选择预设
4. 生成 HTML 幻灯片
5. 按需部署或导出

### 配音模式

1. 调用 `$audio-slides`
2. 告诉 Skill 你需要配音或字幕
3. 如果本地还没有配置豆包 V3，就先填写配置
4. 运行 `clone-status`
5. 如果音色还没准备好，运行 `clone-train`
6. 运行一次 live `probe`
7. 再生成完整配音资产和最终幻灯片

## 首次配置豆包 V3

先创建本地配置文件：

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\config\providers\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

然后填写这些字段：

- `credentials.app_id`
- `credentials.access_key`
- `clone.speaker_id`
- `clone.voice_type`
- `synthesis.voice_type`
- `synthesis.resource_id`

其中 `speaker_id` 和 `voice_type` 由最终用户自己选择或提供。仓库不会把真实生产音色 ID 写死。

## 常用命令

### 查询音色状态

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
```

### 上传训练样本

```powershell
py .\scripts\tts_generator.py clone-train `
  --config .\.audio-slides\tts-provider.json `
  --audio .\sample.wav `
  --demo-text "This is the preview sentence."
```

### 运行真机 Probe

```powershell
py .\scripts\tts_generator.py probe `
  --config .\.audio-slides\tts-provider.json `
  --text "Audio Slides live probe."
```

### 生成整套配音资产

```powershell
py .\scripts\tts_generator.py synthesize `
  --config .\.audio-slides\tts-provider.json `
  --script .\narration-plan.json `
  --output-dir .\.audio-slides\generated
```

## Narration Plan 示例

```json
{
  "deck_title": "Audio Slides Demo",
  "slides": [
    {
      "slide_index": 1,
      "slide_id": "slide-01",
      "title": "Opening",
      "narration": "欢迎来到 Audio Slides，这套演示支持旁白和字幕。"
    }
  ]
}
```

## 输出结构

纯视觉模式下，通常还是单个 HTML 文件。

带配音时，通常会输出：

```text
deck.html
deck-assets/
  narration-manifest.json
  narration.vtt
  narration.srt
  slide-01.mp3
  slide-02.mp3
```

## 配音服务支持情况

为了避免 README 和实际代码不一致，这里明确区分“已实现”和“规划中”。

| 服务 | 状态 | 说明 |
| --- | --- | --- |
| 豆包 Doubao V3 | 已实现 | 音色训练、状态查询、升级、probe、旁白生成 |
| Lipvoice | 规划中 | 低成本扩展方向 |
| Azure AI Speech | 规划中 | 企业和多语言方向 |
| Minimax | 规划中 | 情感表达方向 |
| Reecho | 规划中 | 低门槛中文复刻方向 |
| Fish Audio | 规划中 | 高拟真方向 |
| LMNT | 规划中 | 低延迟方向 |
| Qwen3-TTS | 规划中 | 云端与本地兼容方向 |
| Edge-TTS | 规划中 | 免费测试兜底方案 |
| 本地开源栈 | 规划中 | 隐私和自托管方向 |

## 字幕策略

### 目前已实现

- 从合成时间信息生成字幕
- 输出 `.srt` 和 `.vtt`
- 通过 `scripts/subtitle_helper.py` 处理字幕文件

### 下一步适合补强的方向

- 豆包兼容的 ASR 对齐
- Whisper / faster-whisper 兜底
- 直接导入用户自己的 SRT / VTT

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| `SKILL.md` | Skill 主流程说明 |
| `STYLE_PRESETS.md` | 继承自原项目的风格预设库 |
| `viewport-base.css` | 继承自原项目的视口适配 CSS |
| `animation-patterns.md` | 继承自原项目的动画参考 |
| `html-template.md` | HTML 架构、内联编辑、图片与音频模板规范 |
| `audio-features.md` | 旁白、字幕、同步、时间轴行为说明 |
| `references/volcengine-doubao.md` | 豆包 V3 配置与接口参考 |
| `scripts/extract-pptx.py` | PPT / PPTX 提取脚本 |
| `scripts/deploy.sh` | Vercel 部署脚本 |
| `scripts/export-pdf.sh` | PDF 导出脚本 |
| `scripts/tts_generator.py` | 豆包 V3 训练、查询、probe、旁白生成脚本 |
| `scripts/subtitle_helper.py` | 字幕生成脚本 |
| `config/providers/volcengine-doubao.example.json` | 本地配置模板 |

## 分享与导出

这个仓库保留了原项目的分享流程：

```powershell
bash .\scripts\deploy.sh .\deck-folder\
bash .\scripts\export-pdf.sh .\deck.html
```

## 路线图建议

后续最有价值的扩展方向：

- 背景音乐与旁白自动闪避
- 演讲者备注与 Presenter Mode
- 带音频的视频导出
- 多厂商 TTS 切换
- 更强的字幕对齐链路
- 多语言配音与多语言 Deck 生成

## 致谢

本仓库基于 [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 的架构和设计思想扩展而来。保留下来的设计系统文件、工作流思路与许可证信息应继续保留原始归属。

## License

MIT.
