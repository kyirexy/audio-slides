---
name: audio-slides
description: Create striking HTML presentations from scratch, by converting PPT/PPTX files, or by enhancing existing slide decks. Use when the user wants style discovery, single-file HTML slides, inline editing, image-aware slide design, PDF or URL sharing, synchronized narration, subtitles, or Doubao V3 clone-voice workflows.
---

# Audio Slides

Create zero-dependency HTML presentations that inherit the full `frontend-slides` workflow and add audio-led delivery with narration, subtitles, voice-clone configuration, and sync-aware playback.

## Core Principles

1. **Preserve the original baseline**. Match or exceed the original `frontend-slides` capability set. Never regress on style discovery, PPT conversion, viewport fit, deploy, or export.
2. **HTML-first delivery**. Prefer a single HTML file. If narration is enabled, allow a sibling asset folder for audio and subtitle files.
3. **Show, do not over-ask**. Generate visual previews and concrete options instead of forcing abstract design vocabulary.
4. **No AI-slop aesthetics**. Push toward deliberate typography, atmosphere, and motion.
5. **Viewport fit is non-negotiable**. Every slide must fit inside `100vh` and `100dvh`. Split content instead of cramming or scrolling.
6. **Audio is optional but first-class**. If narration is chosen, the deck structure, narration script, subtitles, and timing should be designed together.

## Design Aesthetics

Avoid generic output. Every deck should feel intentionally designed for its context.

Focus on:

- typography that feels distinctive instead of default,
- strong theme contrast and disciplined use of accents,
- one or two high-impact motion ideas instead of scattered gimmicks,
- backgrounds with atmosphere, depth, or texture,
- presentation chrome that feels integrated when audio is enabled.

Avoid:

- Inter, Roboto, Arial, or other default-safe fonts unless the existing brand requires them,
- timid light-purple-on-white palettes,
- predictable SaaS card layouts,
- stuffing subtitle or transport UI inside already dense slides.

## Viewport Rules

These apply to every generated or modified deck:

- every `.slide` must have `height: 100vh; height: 100dvh; overflow: hidden;`
- all font sizes and spacing must use `clamp(...)`
- content containers need `max-height` constraints
- images must respect `max-height: min(50vh, 400px)`
- include breakpoints for heights `700px`, `600px`, and `500px`
- include `prefers-reduced-motion` support
- never negate CSS functions directly; use `calc(-1 * clamp(...))` instead

When generating, always read [`viewport-base.css`](viewport-base.css) and include its full contents in the final HTML.

### Content Density Limits

| Slide Type | Maximum Content |
| --- | --- |
| Title slide | 1 heading + 1 subtitle + optional tagline |
| Content slide | 1 heading + 4-6 bullets or 2 paragraphs |
| Feature grid | 1 heading + up to 6 cards |
| Code slide | 1 heading + 8-10 lines of code |
| Quote slide | 1 quote + attribution |
| Image slide | 1 heading + 1 image |

If content exceeds the limit, split it into more slides.

## Phase 0: Detect Mode

Determine the user intent:

- **Mode A: New presentation**
- **Mode B: PPT/PPTX conversion**
- **Mode C: Enhancement of an existing HTML deck**

If narration, subtitles, uploaded audio, or voice cloning are requested, also run the audio phases below.

### Mode C: Modification Rules

When enhancing an existing deck:

1. Audit the current slide density before adding content.
2. Never add content that introduces scrolling.
3. When adding images, verify `max-height` rules and split slides if needed.
4. When adding narration later, keep subtitle and transport UI in presentation chrome rather than inside crowded slide bodies.
5. If autoplay is enabled, audio is the source of truth; otherwise manual navigation remains primary.

## Phase 1: Discovery

Ask one compact batch of questions that covers:

- presentation purpose,
- approximate length,
- source content state,
- whether inline browser editing is needed,
- whether images or brand assets exist,
- whether narration is needed,
- whether subtitles are needed,
- whether slides should auto-advance with audio,
- whether the user already has audio or wants AI narration,
- whether the user already has a trained Doubao voice clone or needs to train one,
- whether background music is needed.

If the user already has content, ask them to paste it or point to the files immediately.

### Step 1.2: Image Evaluation

If images are provided:

1. Scan the folder and list the image files.
2. View and evaluate each image.
3. Mark each image as usable or not usable with a reason.
4. Co-design the outline around the available images and text.
5. If a logo is good enough, reuse it in style previews and final deck branding.

Do not treat images as an afterthought. They should influence the slide outline.

## Phase 1.5: Narration Bootstrap

Run this phase only when narration, subtitles, or voice-clone use is requested.

### Provider Selection

Recommend this default path first:

- `Volcengine Doubao V3`

### First-Run Configuration

If no local provider config exists, create one from [`volcengine-doubao.example.json`](volcengine-doubao.example.json).

Use a local ignored file such as:

- `.audio-slides/tts-provider.json`

If the config is missing, stop and ask for one compact credential batch:

- `app_id`
- `access_key`
- `speaker_id`
- `resource_id` with `seed-icl-2.0` as the default suggestion
- `voice_type`
- optional training audio path if the user has not trained the voice yet

Let the user choose the `speaker_id` and `voice_type`. Do not hardcode production voice identifiers into the repository.

If the user does not yet have a working clone voice:

1. Ask for a clean training audio file.
2. Run `clone-train`.
3. Poll `clone-status` until status is `2` or `4`.
4. If needed, run `clone-upgrade`.
5. Only then run the live synthesis probe.

### Probe Before Full Generation

Before generating a full narrated deck, run:

```powershell
py .\scripts\tts_generator.py clone-status --config .\.audio-slides\tts-provider.json
py .\scripts\tts_generator.py probe --config .\.audio-slides\tts-provider.json --text "Audio Slides live probe."
```

If the probe fails, stop and show the exact provider error. Fix credentials, resource choice, or voice identifiers before continuing.

### Provider Reference

When the chosen provider is Doubao, read:

- [`volcengine-doubao.md`](volcengine-doubao.md)

## Phase 2: Style Discovery

This should preserve the original `frontend-slides` feel: let users react to visuals.

### Step 2.0: Style Path

Ask how they want to choose:

- `Show me options` for three previews
- `I know what I want` for direct preset selection

If they pick directly, use [`STYLE_PRESETS.md`](STYLE_PRESETS.md).

### Step 2.1: Mood Selection

Ask what feeling the audience should have:

- impressed / confident
- excited / energized
- calm / focused
- inspired / moved

### Step 2.2: Generate 3 Style Previews

Generate three clearly different single-slide HTML previews that show:

- typography,
- colors,
- animation pacing,
- overall composition,
- subtitle band and transport styling when narration is enabled.

Save previews under `.claude-design/slide-previews/` or a similar local preview folder.

### Step 2.3: User Picks

Let the user:

- pick one preview,
- request a blend,
- or choose a preset directly.

## Phase 3: Outline And Script

Design the slide outline before generating the final HTML.

If narration is enabled:

1. Write slide copy and narration together.
2. Keep narration concise enough for reliable TTS calls.
3. Prefer 1 to 3 spoken beats per slide.
4. Split long explanations into more slides.

Narration guidance:

- opening slide: one concise hook,
- content slide: one framing sentence plus key points,
- closing slide: one summary or call to action.

## Phase 4: Generate Presentation

Before generating, read:

- [`html-template.md`](html-template.md)
- [`viewport-base.css`](viewport-base.css)
- [`animation-patterns.md`](animation-patterns.md)

Read [`audio-features.md`](audio-features.md) only when the deck includes narration, subtitles, uploaded audio, or auto-sync behavior.

Required output rules:

- inline all CSS and JS into the HTML,
- copy the full contents of `viewport-base.css`,
- use expressive web fonts instead of system defaults,
- preserve keyboard and touch navigation,
- include clear section comments.

When narration is off:

- keep the output as a single HTML file.

When narration is on:

- generate `deck.html`,
- generate a sibling asset folder for audio and subtitle files,
- keep asset paths relative.

## Phase 5: PPT/PPTX Conversion

When converting PowerPoint files:

1. Run `py .\scripts\extract-pptx.py <input.pptx> <output_dir>`.
2. Confirm the extracted content with the user.
3. Continue into style discovery.
4. Generate HTML while preserving text, images, slide order, and speaker notes.

## Phase 6: Audio Asset Generation

Run this only for narrated decks.

### Build Narration Plan

Create a narration plan JSON with one item per slide.

### Generate Audio

Use:

```powershell
py .\scripts\tts_generator.py synthesize --config .\.audio-slides\tts-provider.json --script .\narration-plan.json --output-dir .\.audio-slides\generated
```

This should produce:

- per-slide audio files,
- `narration-manifest.json`,
- `.srt` and `.vtt` subtitle files,
- an optional combined audio file if `ffmpeg` is available.

### If User Supplies Their Own Audio

Skip TTS generation and instead:

1. ask for the audio file and subtitle file if available,
2. if no subtitle file exists, create a coarse slide timeline,
3. wire the HTML to use those uploaded assets as the sync source.

## Phase 7: Delivery

Always tell the user:

- where the generated HTML lives,
- whether the output is single-file or HTML-plus-assets,
- how navigation works,
- how subtitle and autoplay behavior work,
- how to swap fonts, colors, voice settings, or timing later.

For narrated decks also describe:

- where `narration-manifest.json` is,
- where `.srt` and `.vtt` are,
- whether combined audio exists,
- whether auto-advance is enabled by default.

## Phase 8: Share Or Export

Preserve the original share flow:

- deploy to a live URL with [`scripts/deploy.sh`](scripts/deploy.sh),
- export to PDF with [`scripts/export-pdf.sh`](scripts/export-pdf.sh).

For narrated decks, prefer deploying the full folder instead of a lone HTML file.

## Supporting Files

| File | Purpose | When to Read |
| --- | --- | --- |
| [`STYLE_PRESETS.md`](STYLE_PRESETS.md) | Visual presets and aesthetic ingredients | Style selection |
| [`viewport-base.css`](viewport-base.css) | Mandatory responsive slide CSS | Every generation |
| [`html-template.md`](html-template.md) | HTML architecture and controller layout | Deck generation |
| [`animation-patterns.md`](animation-patterns.md) | Motion snippets and pacing ideas | Deck generation |
| [`audio-features.md`](audio-features.md) | Audio sync, subtitles, waveform, and transport behavior | Narrated decks |
| [`volcengine-doubao.md`](volcengine-doubao.md) | Doubao V3 config and API notes | Doubao setup |
| [`scripts/extract-pptx.py`](scripts/extract-pptx.py) | PPT extraction | PPT conversion |
| [`scripts/tts_generator.py`](scripts/tts_generator.py) | V3 clone training, status, probe, and narration generation | AI narration |
| [`scripts/subtitle_helper.py`](scripts/subtitle_helper.py) | Subtitle generation and conversion | Subtitle output |
| [`scripts/deploy.sh`](scripts/deploy.sh) | Deploy to Vercel | Sharing |
| [`scripts/export-pdf.sh`](scripts/export-pdf.sh) | Export to PDF | Sharing |
