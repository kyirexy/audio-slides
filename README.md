# Audio Slides

`audio-slides` is a presentation skill for Codex or Claude Code. It inherits the full `frontend-slides` baseline and adds narration, subtitles, synchronized playback, and Doubao V3 clone-voice workflows.

## Capability Coverage

This repository is intended to be strictly stronger than the original `frontend-slides`, not weaker. It keeps:

- presentation creation from scratch,
- PPT/PPTX conversion,
- enhancement of existing HTML decks,
- style discovery with presets and previews,
- strict viewport-fit rules,
- inline editing guidance,
- deploy-to-URL support,
- PDF export support.

It adds:

- Doubao V3 clone voice setup,
- live voice probe commands,
- subtitle generation from synthesis timing,
- audio-aware deck structure,
- transport and subtitle chrome guidance,
- narration manifest generation.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Main skill workflow |
| `STYLE_PRESETS.md` | Visual preset library inherited from the original project |
| `viewport-base.css` | Viewport-fit baseline CSS inherited from the original project |
| `animation-patterns.md` | Animation reference inherited from the original project |
| `html-template.md` | HTML architecture, inline editing, image, and audio guidance |
| `audio-features.md` | Narration, subtitles, sync, and timeline behavior |
| `references/volcengine-doubao.md` | Doubao V3 setup notes and API references |
| `scripts/extract-pptx.py` | PPT/PPTX extraction |
| `scripts/deploy.sh` | Vercel deployment helper |
| `scripts/export-pdf.sh` | PDF export helper |
| `scripts/tts_generator.py` | Doubao V3 clone train, status, probe, and narration generation |
| `scripts/subtitle_helper.py` | Subtitle file generation from narration manifests |
| `config/providers/volcengine-doubao.example.json` | Example local provider config |

## Installation

### Codex

Clone this repository into your Codex skills directory:

```powershell
git clone https://github.com/kyirexy/audio-slides "$env:USERPROFILE\.codex\skills\audio-slides"
```

Then invoke it as:

```text
$audio-slides
```

### Claude Code

If you use Claude Code style local skills, clone or copy the repository into your skill directory and invoke it with the matching skill name used by your environment.

## First Run

On the first narrated run, the skill should:

1. ask whether the user wants pure visual slides or narrated slides,
2. ask for Doubao V3 credentials if narration is enabled and no local config exists,
3. ask the user to choose or provide `speaker_id`, `voice_type`, and `resource_id`,
4. run `clone-status`,
5. if needed, run `clone-train`,
6. run a live `probe`,
7. only then generate the full narrated deck.

Real secrets should live in:

```text
.audio-slides/tts-provider.json
```

That file is ignored by git.

## Doubao V3 Local Config

Create the local config by copying the example:

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\config\providers\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

Fill these fields:

- `credentials.app_id`
- `credentials.access_key`
- `clone.speaker_id`
- `clone.voice_type`
- `synthesis.voice_type`
- `synthesis.resource_id`

The user should choose the real voice identifiers when they use the skill. They are not hardcoded in the repository.

## Live Probe

Check clone status:

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
```

If the voice is not trained yet:

```powershell
py .\scripts\tts_generator.py clone-train `
  --config .\.audio-slides\tts-provider.json `
  --audio .\sample.wav `
  --demo-text "This is the preview sentence."
```

Run a live synthesis probe:

```powershell
py .\scripts\tts_generator.py probe `
  --config .\.audio-slides\tts-provider.json `
  --text "Audio Slides live probe."
```

## Narration Generation

Prepare a narration plan:

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

Generate narration assets:

```powershell
py .\scripts\tts_generator.py synthesize `
  --config .\.audio-slides\tts-provider.json `
  --script .\narration-plan.json `
  --output-dir .\.audio-slides\generated
```

## Output Model

Visual-only decks remain a single HTML file.

Narrated decks typically ship as:

```text
deck.html
deck-assets/
  narration-manifest.json
  narration.vtt
  narration.srt
  slide-01.mp3
  slide-02.mp3
```

## Sharing

This repository keeps the original share workflow:

```powershell
bash .\scripts\deploy.sh .\deck-folder\
bash .\scripts\export-pdf.sh .\deck.html
```

## Attribution

This repository is intentionally bootstrapped from the architecture of `frontend-slides` by [@zarazhangrui](https://github.com/zarazhangrui). Reused design-system files and workflow ideas should retain attribution and license context.

## License

MIT.
