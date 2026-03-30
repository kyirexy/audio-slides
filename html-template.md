# HTML Presentation Template

Reference architecture for `audio-slides`. Visual-only decks still follow the original single-file rule. Narrated decks add a thin transport layer and asset manifest.

## Base Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Deck Title</title>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&family=Cormorant+Garamond:wght@500;700&display=swap" />

  <style>
    /* === THEME TOKENS === */
    :root {
      --bg-base: #0b1020;
      --bg-elevated: rgba(12, 18, 36, 0.78);
      --text-strong: #f8fafc;
      --text-soft: rgba(232, 240, 255, 0.78);
      --accent: #62f5c8;
      --accent-2: #7cc5ff;
      --subtitle-bg: rgba(4, 10, 24, 0.82);
      --transport-bg: rgba(8, 15, 31, 0.76);
      --glow: 0 0 40px rgba(124, 197, 255, 0.18);
      --title-size: clamp(2.5rem, 7vw, 5.5rem);
      --body-size: clamp(0.9rem, 1.3vw, 1.1rem);
      --slide-padding: clamp(1.5rem, 4vw, 4rem);
    }

    /* === VIEWPORT RULES === */
    /* Paste the full viewport-base.css contents here. */

    /* === AMBIENT BACKGROUND === */
    body::before,
    body::after {
      content: "";
      position: fixed;
      inset: auto;
      pointer-events: none;
      z-index: 0;
      filter: blur(24px);
    }

    body::before {
      top: -10vh;
      right: -8vw;
      width: 40vw;
      height: 40vw;
      background: radial-gradient(circle, rgba(98, 245, 200, 0.18), transparent 70%);
    }

    body::after {
      bottom: -12vh;
      left: -6vw;
      width: 34vw;
      height: 34vw;
      background: radial-gradient(circle, rgba(124, 197, 255, 0.22), transparent 70%);
    }

    /* === GLOBAL CHROME === */
    .progress-bar,
    .subtitle-band,
    .transport,
    .nav-dots {
      position: fixed;
      z-index: 20;
    }

    .subtitle-band {
      left: 50%;
      bottom: clamp(1rem, 2vw, 1.8rem);
      transform: translateX(-50%);
      width: min(86vw, 980px);
      min-height: 3.2rem;
      padding: 0.8rem 1rem;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 1rem;
      background: var(--subtitle-bg);
      color: var(--text-strong);
      backdrop-filter: blur(20px);
      box-shadow: var(--glow);
    }

    .transport {
      top: clamp(0.8rem, 2vw, 1.4rem);
      right: clamp(0.8rem, 2vw, 1.4rem);
      display: grid;
      gap: 0.65rem;
      width: min(28rem, 86vw);
      padding: 0.9rem 1rem;
      border-radius: 1rem;
      background: var(--transport-bg);
      border: 1px solid rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(20px);
    }

    .waveform {
      width: 100%;
      height: 40px;
      border-radius: 999px;
      background:
        linear-gradient(90deg, rgba(98, 245, 200, 0.26), rgba(124, 197, 255, 0.1)),
        rgba(255, 255, 255, 0.04);
    }
  </style>
</head>
<body>
  <!-- === PRESENTATION CHROME === -->
  <div class="progress-bar" aria-hidden="true"></div>
  <nav class="nav-dots" aria-label="Slide navigation"></nav>

  <!-- === OPTIONAL AUDIO UI === -->
  <aside class="transport" data-audio-ui hidden>
    <div class="now-playing">
      <strong>Now Playing</strong>
      <span data-current-slide-label>Opening</span>
    </div>
    <canvas class="waveform" data-waveform></canvas>
    <div class="timeline">
      <button type="button" data-audio-toggle>Play</button>
      <input type="range" min="0" max="100" value="0" data-audio-seek />
    </div>
  </aside>
  <div class="subtitle-band" data-subtitle hidden></div>

  <!-- === SLIDES === -->
  <main class="deck-shell">
    <section class="slide title-slide" data-slide-id="slide-01">
      <div class="hero">
        <p class="eyebrow reveal">Category</p>
        <h1 class="reveal">Deck Title</h1>
        <p class="lead reveal">Narrated HTML presentations with subtitles and cinematic motion.</p>
      </div>
    </section>

    <section class="slide" data-slide-id="slide-02">
      <div class="slide-grid">
        <div>
          <h2 class="reveal">Key Point</h2>
          <p class="reveal">Keep copy short enough that narration, subtitles, and layout can breathe together.</p>
        </div>
      </div>
    </section>
  </main>

  <!-- === OPTIONAL AUDIO ASSETS === -->
  <audio data-master-audio preload="metadata"></audio>

  <script>
    /* === MANIFEST PLACEHOLDER === */
    const narrationManifest = null;

    /* === SLIDE CONTROLLER === */
    class SlidePresentation {
      constructor() {
        this.slides = [...document.querySelectorAll('.slide')];
        this.currentSlide = 0;
        this.setupVisibility();
        this.setupKeyboard();
        this.setupTouch();
        this.setupNavDots();
      }

      goToSlide(index, { behavior = 'smooth' } = {}) {
        const bounded = Math.max(0, Math.min(index, this.slides.length - 1));
        this.currentSlide = bounded;
        this.slides[bounded].scrollIntoView({ behavior, block: 'start' });
        this.syncActiveState();
      }
    }

    /* === AUDIO CONTROLLER === */
    class AudioNarrationController {
      constructor(presentation, manifest) {
        this.presentation = presentation;
        this.manifest = manifest;
        this.audio = document.querySelector('[data-master-audio]');
        this.subtitleNode = document.querySelector('[data-subtitle]');
      }

      init() {
        if (!this.manifest) return;
        document.querySelector('[data-audio-ui]').hidden = false;
        this.subtitleNode.hidden = false;
        this.audio.addEventListener('timeupdate', () => this.syncFromTime());
      }

      syncFromTime() {
        // Read current time, update subtitle cue, and auto-advance slides
        // only when autoplay is enabled for this deck.
      }

      seekToSlide(slideIndex) {
        // Jump audio timeline when manual navigation explicitly requests sync.
      }
    }

    /* === AMBIENT MOTION === */
    class AmbientBackground {
      constructor() {
        this.pointer = { x: 0.5, y: 0.5 };
      }

      init() {
        window.addEventListener('pointermove', (event) => {
          this.pointer.x = event.clientX / window.innerWidth;
          this.pointer.y = event.clientY / window.innerHeight;
          document.documentElement.style.setProperty('--pointer-x', this.pointer.x.toFixed(3));
          document.documentElement.style.setProperty('--pointer-y', this.pointer.y.toFixed(3));
        });
      }
    }

    const presentation = new SlidePresentation();
    new AmbientBackground().init();
    new AudioNarrationController(presentation, narrationManifest).init();
  </script>
</body>
</html>
```

## Required Controllers

Every generated deck should include:

1. `SlidePresentation`
2. `AmbientBackground`
3. `AudioNarrationController` when narration or uploaded audio exists
4. Inline editing logic only when the user explicitly asks for editable text

## Required JavaScript Features

Every generated deck must preserve the original `frontend-slides` baseline:

1. keyboard navigation for arrows, space, and page keys
2. touch and swipe navigation
3. mouse wheel navigation when appropriate
4. progress bar updates
5. navigation dots
6. intersection-observer-based reveal animations

Optional enhancements should match the chosen style:

- custom cursor or pointer glow,
- particle or canvas background,
- parallax motion,
- 3D tilt,
- counter animation,
- audio waveform or subtitle highlight.

## Inline Editing Implementation

Only include inline editing when the user explicitly asks for editable text.

Required behavior:

- toggle button for edit mode,
- hover hotzone or keyboard shortcut to reveal the toggle,
- auto-save to local storage,
- export or save behavior for edited content.

Do not rely on a CSS-only sibling hover trick for the edit toggle. Use JavaScript-controlled show and hide behavior with a short grace period so the button remains clickable.

## Image Pipeline

When the deck includes user images:

- resize overly large images before embedding them,
- use direct relative file paths instead of base64 for large image assets,
- keep `max-height: min(50vh, 400px)`,
- adapt border, shadow, and framing to the chosen style,
- do not repeat the same screenshot on multiple slides unless it is a logo.

If the user has no images, CSS-generated visuals are still a valid first-class path.

## Audio Integration

When narration is enabled:

- treat subtitles and transport as fixed presentation chrome,
- load timing from `narration-manifest.json`,
- support manual override even when autoplay exists,
- keep waveform and subtitle UI out of the slide content area,
- allow the user to disable autoplay without breaking playback.

## Visual Guidance

Push the deck beyond plain fade-ins:

- use layered gradients, shapes, or canvas-based atmospherics,
- let subtitle and transport chrome feel designed, not bolted on,
- use staggered reveals and one high-impact motion idea per deck,
- prefer strong theme contrast over timid neutral palettes.

## Narrated Deck Rules

When narration is enabled:

- audio timing is the source of truth only if autoplay is enabled,
- subtitles belong in presentation chrome, not inside the slide body,
- deck assets should stay relative to the HTML file,
- waveform and transport elements must not cover essential slide content,
- always provide a manual override so users can disable autoplay and navigate freely.

## File Model

Visual-only:

```text
deck.html
```

Narrated:

```text
deck.html
deck-assets/
  narration-manifest.json
  narration.vtt
  narration.srt
  slide-01.mp3
  slide-02.mp3
```

## Code Quality

- use semantic HTML,
- keep keyboard navigation working,
- include `prefers-reduced-motion`,
- add section comments that explain what can be customized later.
