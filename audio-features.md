# Audio Features

Use this file only when the deck includes narration, subtitles, uploaded audio, or sync-driven navigation.

## Output Contract

Narrated decks should emit:

- `deck.html`
- `deck-assets/narration-manifest.json`
- `deck-assets/narration.vtt`
- `deck-assets/narration.srt`
- one audio segment per slide
- an optional combined narration track if `ffmpeg` is available

## Narration Manifest Shape

```json
{
  "provider": "volcengine-doubao",
  "generated_at": "2026-03-30T17:00:00Z",
  "audio_encoding": "mp3",
  "combined_audio": "narration-full.mp3",
  "slides": [
    {
      "slide_index": 1,
      "slide_id": "slide-01",
      "title": "Opening",
      "text": "Welcome to Audio Slides.",
      "audio_file": "slide-01.mp3",
      "duration_ms": 2150,
      "start_ms": 0,
      "end_ms": 2150,
      "words": [
        {
          "word": "Welcome",
          "start_ms": 10,
          "end_ms": 420
        }
      ]
    }
  ]
}
```

## Sync Rules

### Audio-Led Mode

Use this when the user explicitly wants autoplay:

- the active slide follows the audio timeline,
- subtitles update from the current cue,
- progress bar reflects narration progress,
- manual slide clicks may seek the audio timeline.

### Manual-Led Mode

Use this when the user wants narration but not forced autoplay:

- audio can play independently,
- slide navigation stays manual,
- clicking a slide marker may optionally seek audio,
- subtitle display can remain active without forcing slide changes.

## Subtitle Strategy

Preferred subtitle sources, in order:

1. word timestamps returned by the TTS provider,
2. user-supplied `.srt` or `.vtt`,
3. coarse slide-level cues derived from the narration script.

Use subtitle chrome, not on-slide paragraphs, for the current spoken line.

## UI Components

Narrated decks can include:

- a compact transport panel,
- a subtitle band,
- a waveform or meter,
- a slide progress rail,
- an "up next" hint during long transitions.

These belong in fixed presentation chrome so they do not break layout density.

## Background Music

If the user wants background music:

- use the Web Audio API,
- route narration and music through separate gain nodes,
- duck the music automatically while narration is active,
- keep music optional and easy to disable.

## Timing Editor

If a user asks for manual timing control, provide a lightweight timeline editor with:

- one row per slide,
- start time input,
- duration preview,
- optional subtitle offset tweak,
- export back to `narration-manifest.json`.

Do not build this editor unless the user asks for it. The first version should prioritize generation and playback.

## Accessibility

- expose subtitle text in semantic HTML,
- keep transport buttons keyboard reachable,
- support `prefers-reduced-motion`,
- never rely on waveform animation alone to communicate playback state.
