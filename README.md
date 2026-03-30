# Audio Slides

[English](./README.md) | [简体中文](./README.zh-CN.md)

A Codex / Claude Code skill for creating striking HTML presentations from scratch, converting PowerPoint files, and adding Doubao V3 narration with subtitles.

## What This Does

`audio-slides` keeps the strongest parts of `frontend-slides` and extends them with audio-first presentation workflows.

### Key Features

- **Zero-dependency slide output**: Generate HTML presentations with inline CSS and JavaScript.
- **Visual style discovery**: Let users choose from previews or presets instead of describing aesthetics abstractly.
- **PPT conversion**: Convert `.ppt` / `.pptx` content into web presentations.
- **Narrated decks**: Generate voice-over assets, subtitle files, and narration manifests.
- **Doubao V3 workflow**: Support clone status checks, clone training, upgrade, live probe, and narration generation.
- **Sharing support**: Keep deploy-to-URL and PDF export helpers from the original project.

## Installation

### For Codex

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

Then invoke it with:

```text
$audio-slides
```

### For Claude Code Style Local Skills

Clone or copy this repository into your local skills directory and invoke it with the matching skill name used by your environment.

## Usage

### Create a New Presentation

```text
$audio-slides

> I want a narrated product presentation for my AI startup
```

The skill will:

1. ask about purpose, length, content, images, editing, narration, and subtitles,
2. guide style selection with previews or presets,
3. generate the HTML presentation,
4. optionally generate Doubao V3 narration assets,
5. optionally deploy the deck or export it to PDF.

### Convert a PowerPoint

```text
$audio-slides

> Convert my presentation.pptx into a narrated web deck
```

The skill will:

1. extract slide content from the PowerPoint file,
2. confirm the extracted structure,
3. rebuild the deck as HTML,
4. optionally add narration and subtitle assets.

## Doubao V3 Setup

Create a local config file:

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\config\providers\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

Fill these fields in `.audio-slides/tts-provider.json`:

- `credentials.app_id`
- `credentials.access_key`
- `clone.speaker_id`
- `clone.voice_type`
- `synthesis.voice_type`
- `synthesis.resource_id`

The user should choose the real `speaker_id` and `voice_type` during setup. They are not hardcoded in the repository.

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

## Current Support

- **Implemented**: Doubao V3 narration workflow
- **Implemented**: subtitle generation from narration timing
- **Planned**: additional TTS and ASR providers

## Requirements

- Codex or Claude Code
- Python for the helper scripts
- A Doubao V3 account if you want narration
- Node.js for deployment and PDF export helpers

## Credits

Built on top of the architecture and design system of [frontend-slides](https://github.com/zarazhangrui/frontend-slides) by [@zarazhangrui](https://github.com/zarazhangrui).

## License

MIT.
