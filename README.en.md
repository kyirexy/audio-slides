# Audio Slides

[简体中文](./README.md) | [English](./README.en.md)

A presentation skill for Claude Code / Codex that creates HTML decks from scratch, converts PowerPoint files, and adds Doubao V3 narration with subtitles when needed.

## What This Does

`audio-slides` keeps the core `frontend-slides` workflow: help non-designers create polished web presentations without needing CSS or JavaScript. This version adds narration, subtitles, and audio-first presentation flows.

### Key Features

- **Zero Dependencies**: Output a single HTML file, with an asset folder only when narration is enabled.
- **Visual Style Discovery**: Let users pick from previews or presets instead of describing aesthetics abstractly.
- **PPT Conversion**: Convert `.ppt` / `.pptx` into web presentations.
- **Narration + Subtitles**: Generate voice-over audio, subtitle files, and `narration-manifest.json`.
- **Doubao V3 Workflow**: Support clone status, clone training, upgrade, live probe, and narration generation.
- **Sharing Support**: Keep deploy-to-URL and PDF export helpers from the original project.

## Installation

### For Claude Code Users

The easiest option is to clone directly into your skills directory:

```bash
git clone https://github.com/kyirexy/audio-slides.git ~/.claude/skills/audio-slides
```

If you prefer to copy the files manually:

```bash
mkdir -p ~/.claude/skills/audio-slides/scripts

cp SKILL.md STYLE_PRESETS.md viewport-base.css html-template.md animation-patterns.md \
  audio-features.md volcengine-doubao.md volcengine-doubao.example.json \
  ~/.claude/skills/audio-slides/

cp scripts/* ~/.claude/skills/audio-slides/scripts/
```

Then invoke it in Claude Code with:

```text
/audio-slides
```

### For Codex Users

Clone directly into the Codex skills directory:

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

Then invoke it with:

```text
$audio-slides
```

## Usage

### Create a New Presentation

```text
/audio-slides

> I want a narrated product presentation for my AI startup
```

The skill will:

1. ask about content, length, images, editing, narration, and subtitles,
2. guide style selection with previews or presets,
3. generate the final HTML deck,
4. optionally generate narration and subtitle assets,
5. optionally deploy or export the result.

### Convert a PowerPoint

```text
/audio-slides

> Convert my presentation.pptx into a narrated web deck
```

The skill will:

1. extract PowerPoint content, images, and notes,
2. confirm the extracted structure,
3. rebuild the deck as HTML,
4. optionally add narration and subtitle assets.

## First-Time Doubao Setup

Before the first narrated run, create the local config:

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

Fill these fields:

- `credentials.app_id`
- `credentials.access_key`
- `clone.speaker_id`
- `clone.voice_type`
- `synthesis.voice_type`
- `synthesis.resource_id`

On the first narrated run, the skill should ask the user to confirm these values before running `clone-status`, `clone-train`, or `probe`.

### Common Commands

Check clone status:

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
```

Train a clone voice:

```powershell
py .\scripts\tts_generator.py clone-train `
  --config .\.audio-slides\tts-provider.json `
  --audio .\sample.wav `
  --demo-text "This is the preview sentence."
```

Run a live probe:

```powershell
py .\scripts\tts_generator.py probe `
  --config .\.audio-slides\tts-provider.json `
  --text "Audio Slides live probe."
```

Generate narration assets:

```powershell
py .\scripts\tts_generator.py synthesize `
  --config .\.audio-slides\tts-provider.json `
  --script .\narration-plan.json `
  --output-dir .\.audio-slides\generated
```

## Architecture

Like `frontend-slides`, this skill uses progressive disclosure: the main `SKILL.md` stays concise, while supporting files are read only when needed.

| File | Purpose | Loaded When |
| --- | --- | --- |
| `SKILL.md` | Core workflow and rules | Skill invocation |
| `STYLE_PRESETS.md` | Style presets | Style selection |
| `viewport-base.css` | Responsive slide CSS | Generation |
| `html-template.md` | HTML structure and interaction template | Generation |
| `animation-patterns.md` | Animation reference | Generation |
| `audio-features.md` | Audio and subtitle behavior | Narrated mode |
| `volcengine-doubao.md` | Doubao V3 notes | Narrated mode |
| `scripts/extract-pptx.py` | PPT extraction | PPT conversion |
| `scripts/deploy.sh` | Deploy to URL | Sharing |
| `scripts/export-pdf.sh` | Export to PDF | Sharing |
| `scripts/tts_generator.py` | Doubao V3 workflow | Narrated mode |

## Requirements

- Claude Code or Codex
- Python
- A Doubao V3 account if you want narration
- Node.js for deployment or PDF export

## Credits

Built on top of the architecture and design system of [frontend-slides](https://github.com/zarazhangrui/frontend-slides) by [@zarazhangrui](https://github.com/zarazhangrui).

## License

MIT.
