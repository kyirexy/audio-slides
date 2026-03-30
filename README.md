# Audio Slides

[简体中文](./README.zh-CN.md) | [English](./README.md)

[![MIT License](https://img.shields.io/badge/license-MIT-0f172a.svg)](./LICENSE)
[![Skill](https://img.shields.io/badge/skill-Codex%20%2F%20Claude%20Code-2563eb.svg)](./SKILL.md)
[![Provider](https://img.shields.io/badge/provider-Doubao%20V3-16a34a.svg)](./references/volcengine-doubao.md)
[![Output](https://img.shields.io/badge/output-HTML%20Slides-f59e0b.svg)](./html-template.md)

Audio Slides is a presentation skill for Codex or Claude Code. It preserves the full `frontend-slides` baseline and adds narration, subtitles, synchronized playback, and Doubao V3 clone-voice workflows.

> The goal of this repository is simple: keep everything the original skill already did well, then extend it with audio-first presentation workflows.

## Why This Repo Exists

`frontend-slides` is already a strong foundation for HTML presentations. This repo keeps that foundation and adds:

- narrated slide generation,
- subtitle and timing artifacts,
- Doubao V3 voice-clone setup,
- probe commands for real provider verification,
- audio-aware HTML template guidance.

## Capability Coverage

This repository is meant to be strictly stronger than the original `frontend-slides`, not weaker.

### Inherited From `frontend-slides`

- Create new presentations from scratch
- Convert PPT and PPTX files into HTML decks
- Enhance existing HTML slide decks
- Use visual style discovery with presets and previews
- Keep strict viewport-fit rules
- Preserve inline editing guidance
- Deploy to a live URL
- Export to PDF

### Added By `audio-slides`

- Doubao V3 clone-voice configuration
- Live voice probe commands
- Narration manifest generation
- Subtitle generation from synthesis timing
- Audio transport and subtitle chrome guidance
- Narrated deck asset layout

## Install

### Codex

Clone the repository into your Codex skill directory:

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

Then invoke it as:

```text
$audio-slides
```

### Claude Code

If you use Claude Code style local skills, clone or copy this repository into your local skills directory and invoke it with the matching skill name used by your environment.

## Quick Start

### Visual-Only Slides

1. Invoke `$audio-slides`
2. Choose a new deck, PPT conversion, or enhancement flow
3. Pick a style path or direct preset
4. Generate the HTML deck
5. Optionally deploy or export it

### Narrated Slides

1. Invoke `$audio-slides`
2. Tell the skill you want narration or subtitles
3. Configure Doubao V3 if no local provider config exists yet
4. Run `clone-status`
5. If needed, run `clone-train`
6. Run a live `probe`
7. Generate narration assets and the final deck

## First-Run Doubao V3 Setup

Create the local provider config:

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

The user should choose the real `speaker_id` and `voice_type` when they use the skill. These identifiers are intentionally not hardcoded in the repository.

## Commands

### Check Clone Status

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
```

### Train A Clone Voice

```powershell
py .\scripts\tts_generator.py clone-train `
  --config .\.audio-slides\tts-provider.json `
  --audio .\sample.wav `
  --demo-text "This is the preview sentence."
```

### Run A Live Probe

```powershell
py .\scripts\tts_generator.py probe `
  --config .\.audio-slides\tts-provider.json `
  --text "Audio Slides live probe."
```

### Generate Narration Assets

```powershell
py .\scripts\tts_generator.py synthesize `
  --config .\.audio-slides\tts-provider.json `
  --script .\narration-plan.json `
  --output-dir .\.audio-slides\generated
```

## Narration Plan Example

```json
{
  "deck_title": "Audio Slides Demo",
  "slides": [
    {
      "slide_index": 1,
      "slide_id": "slide-01",
      "title": "Opening",
      "narration": "Welcome to Audio Slides. This deck includes narration and subtitles."
    }
  ]
}
```

## Output Model

Visual-only decks remain a single HTML file.

Narrated decks typically use:

```text
deck.html
deck-assets/
  narration-manifest.json
  narration.vtt
  narration.srt
  slide-01.mp3
  slide-02.mp3
```

## Provider Support

The repository should not claim support that does not exist in code yet, so the matrix below separates current support from roadmap items.

| Provider | Status | Notes |
| --- | --- | --- |
| Doubao V3 | Implemented | Clone status, clone training, upgrade, probe, narration synthesis |
| Lipvoice | Planned | Good low-cost expansion target |
| Azure AI Speech | Planned | Good enterprise and multilingual target |
| Minimax | Planned | Good emotional TTS target |
| Reecho | Planned | Good low-friction Chinese clone path |
| Fish Audio | Planned | Good realism-focused target |
| LMNT | Planned | Good low-latency target |
| Qwen3-TTS | Planned | Good cloud plus local path |
| Edge-TTS | Planned | Good free testing fallback |
| Local open-source stack | Planned | Good privacy and self-host path |

## Subtitle Strategy

### Implemented Now

- subtitle generation from synthesis timing in the narration manifest
- `.srt` and `.vtt` emission through `scripts/subtitle_helper.py`

### Good Next Steps

- Doubao-compatible ASR alignment
- Whisper or faster-whisper fallback
- user-supplied SRT or VTT import

## Repository Layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Main skill workflow |
| `STYLE_PRESETS.md` | Visual presets inherited from the original project |
| `viewport-base.css` | Viewport-fit baseline CSS inherited from the original project |
| `animation-patterns.md` | Animation reference inherited from the original project |
| `html-template.md` | HTML architecture, inline editing, image, and audio guidance |
| `audio-features.md` | Narration, subtitles, sync, and timeline behavior |
| `references/volcengine-doubao.md` | Doubao V3 setup notes and API references |
| `scripts/extract-pptx.py` | PPT and PPTX extraction |
| `scripts/deploy.sh` | Vercel deployment helper |
| `scripts/export-pdf.sh` | PDF export helper |
| `scripts/tts_generator.py` | Doubao V3 clone train, status, probe, and narration generation |
| `scripts/subtitle_helper.py` | Subtitle file generation from narration manifests |
| `config/providers/volcengine-doubao.example.json` | Example local provider config |

## Share And Export

This repository keeps the original share workflow:

```powershell
bash .\scripts\deploy.sh .\deck-folder\
bash .\scripts\export-pdf.sh .\deck.html
```

## Roadmap Ideas

High-value next steps for this repository:

- background music plus narration ducking
- speaker notes and presenter mode
- video export with audio
- multi-provider TTS switching
- stronger subtitle alignment paths
- multilingual deck and narration generation

## Attribution

This repository is intentionally bootstrapped from the architecture of `frontend-slides` by [@zarazhangrui](https://github.com/zarazhangrui). Reused design-system files and workflow ideas should retain attribution and license context.

## License

MIT.
