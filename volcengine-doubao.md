# Volcengine Doubao V3

Use this note only when the deck needs narration through Doubao V3.

## What The Repo Uses

This repository uses the real V3 endpoints for:

- clone training,
- clone status queries,
- clone upgrade,
- live narration probe,
- narration generation.

## Required Values

The user needs to provide:

- `app_id`
- `access_key`
- `speaker_id`
- `voice_type`
- `resource_id`

The example local config lives at:

- [`volcengine-doubao.example.json`](./volcengine-doubao.example.json)

## Local Setup

Copy the example config to the local ignored file:

```powershell
New-Item -ItemType Directory -Force .audio-slides | Out-Null
Copy-Item .\volcengine-doubao.example.json .\.audio-slides\tts-provider.json
```

Then fill the real values before running probe or synthesis.

## Common Commands

Check clone status:

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
```

Run a live probe:

```powershell
py .\scripts\tts_generator.py probe --config .\.audio-slides\tts-provider.json --text "Audio Slides live probe."
```

Generate narration assets:

```powershell
py .\scripts\tts_generator.py synthesize --config .\.audio-slides\tts-provider.json --script .\narration-plan.json --output-dir .\.audio-slides\generated
```
