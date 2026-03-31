# Audio Slides

[简体中文](./README.md) | [English](./README.en.md)

A Codex / Claude Code skill for creating HTML presentations from scratch, converting PowerPoint files, and adding Doubao V3 narration with subtitles when needed.

## What This Does

`audio-slides` keeps the core `frontend-slides` workflow and adds audio support.

### Key Features

- **Zero-dependency output**: Generate a single HTML deck, with an asset folder only when narration is enabled.
- **Style discovery**: Choose from previews or presets.
- **PPT conversion**: Convert `.ppt` / `.pptx` into HTML presentations.
- **Narration and subtitles**: Generate voice-over assets, subtitle files, and `narration-manifest.json`.
- **Doubao V3 workflow**: Support clone status, clone training, upgrade, live probe, and narration generation.
- **Sharing support**: Keep deploy-to-URL and PDF export from the original project.

## Installation

### Codex

Clone directly into the skills directory:

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

Then invoke it with:

```text
$audio-slides
```

### Claude Code Style Local Skills

If you use a local skills directory, clone or copy this repository there and invoke it with the matching skill name used by your environment.

## Usage

### Create A New Presentation

```text
$audio-slides

> I want a narrated product presentation for my AI startup
```

The skill will:

1. ask about content, length, images, editing, narration, and subtitles,
2. help with style selection,
3. generate the HTML deck,
4. optionally generate narration and subtitle assets,
5. optionally deploy or export the result.

### Convert A PowerPoint

```text
$audio-slides

> Convert my presentation.pptx into a narrated web deck
```

The skill will:

1. extract PowerPoint content,
2. confirm the extracted structure,
3. rebuild the deck as HTML,
4. optionally add narration and subtitle assets.

## Doubao V3 Setup

Create the local config file on first use:

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

Required fields:

- `credentials.app_id`
- `credentials.access_key`
- `clone.speaker_id`
- `clone.voice_type`
- `synthesis.voice_type`
- `synthesis.resource_id`

Common commands:

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
py .\scripts\tts_generator.py probe --config .\.audio-slides\tts-provider.json --text "Audio Slides live probe."
py .\scripts\tts_generator.py synthesize --config .\.audio-slides\tts-provider.json --script .\narration-plan.json --output-dir .\.audio-slides\generated
```

For more detail, see [volcengine-doubao.md](./volcengine-doubao.md).

## Repository Layout

The repository intentionally stays close to the original project's shape:

- `SKILL.md`
- `STYLE_PRESETS.md`
- `viewport-base.css`
- `html-template.md`
- `animation-patterns.md`
- `audio-features.md`
- `volcengine-doubao.md`
- `volcengine-doubao.example.json`
- `scripts/`

## Requirements

- Codex or Claude Code
- Python
- A Doubao V3 account if you want narration
- Node.js for deployment and PDF export

## Credits

Built on top of the architecture and design system of [frontend-slides](https://github.com/zarazhangrui/frontend-slides) by [@zarazhangrui](https://github.com/zarazhangrui).

## License

MIT.
