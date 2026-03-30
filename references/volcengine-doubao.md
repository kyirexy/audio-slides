# Volcengine Doubao Setup Notes

Use this reference only when the narration provider is `Volcengine Doubao`.

## Recommended Initial Path

Use the real V3 endpoints:

- voice clone training: `https://openspeech.bytedance.com/api/v3/tts/voice_clone`
- voice clone status: `https://openspeech.bytedance.com/api/v3/tts/get_voice`
- voice clone upgrade: `https://openspeech.bytedance.com/api/v3/tts/upgrade_voice`
- synthesis probe / narration: `https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse`

## Required Fields

You need these values on first load:

- `app_id`
- `access_key`
- `speaker_id`
- `resource_id`
- `voice_type`

If the user has no working `speaker_id` yet, ask whether they want to:

- train an existing voice clone from a sample audio file, or
- use a previously created voice from the console.

The repository example config lives at:

- [`config/providers/volcengine-doubao.example.json`](../config/providers/volcengine-doubao.example.json)

## Current API Notes

Based on Volcengine's official documentation:

- voice clone V3 training and status use the headers `X-Api-App-Key`, `X-Api-Access-Key`, and `X-Api-Request-Id`
- V3 synthesis uses `X-Api-App-Id`, `X-Api-Access-Key`, `X-Api-Request-Id`, and `X-Api-Resource-Id`
- `X-Api-Resource-Id` selects the synthesis effect and billing path
- the user should prefer V3 training plus V3 synthesis for reusable clone voices
- for the main clone effect choices:
  - `seed-icl-1.0`
  - `seed-icl-1.0-concurr`
  - `seed-icl-2.0`
- `speaker_id` is required for clone training and status queries
- `voice_type` is required for synthesis; keep it configurable because some console flows expose a dedicated synthesis voice id

For narrated decks, default to:

- `resource_id`: `seed-icl-2.0`
- `format`: `mp3`
- `sample_rate`: `24000`
- `enable_subtitle`: `true`

## Suggested Defaults

- `speech_rate`: `0`
- `silence_duration`: `150`
- `language`: `0`

## Probe Command

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
py .\scripts\tts_generator.py probe --config .\.audio-slides\tts-provider.json --text "Audio Slides live probe."
```

## Official Sources

- [声音复刻API-V1（含迁移提示与 V3 合成入口表）](https://www.volcengine.com/docs/6561/1305191)
- [V3 WebSocket 双向流式文档](https://www.volcengine.com/docs/6561/1329505)
- [V3 WebSocket/HTTP/SSE 单向流式文档](https://www.volcengine.com/docs/6561/1598757)
