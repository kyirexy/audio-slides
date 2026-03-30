#!/usr/bin/env python3
"""Build subtitle files from a narration manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def format_timestamp(milliseconds: int, *, vtt: bool) -> str:
    hours, remainder = divmod(max(milliseconds, 0), 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1_000)
    separator = "." if vtt else ","
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{millis:03d}"


def normalize_text(value: str) -> str:
    return " ".join(str(value or "").split()).strip()


def join_tokens(tokens: list[str]) -> str:
    parts: list[str] = []
    for token in tokens:
        if not token:
            continue
        if parts:
            last_char = parts[-1][-1]
            next_char = token[0]
            if last_char.isascii() and last_char.isalnum() and next_char.isascii() and next_char.isalnum():
                parts.append(" ")
        parts.append(token)
    return "".join(parts)


def should_flush(buffer_text: str, token: str, max_chars: int) -> bool:
    punctuation = "。！？!?；;，,"
    return token.endswith(tuple(punctuation)) or len(buffer_text) >= max_chars


def build_cues_from_manifest(manifest: dict, *, max_chars: int = 26) -> list[dict]:
    cues: list[dict] = []
    cue_index = 1

    for slide in manifest.get("slides", []):
        words = slide.get("words") or []
        if not words:
            start_ms = int(slide.get("start_ms", 0))
            end_ms = int(slide.get("end_ms", start_ms + 1200))
            text = normalize_text(slide.get("text", ""))
            if text:
                cues.append(
                    {
                        "index": cue_index,
                        "start_ms": start_ms,
                        "end_ms": max(end_ms, start_ms + 600),
                        "text": text,
                        "slide_index": slide.get("slide_index"),
                    }
                )
                cue_index += 1
            continue

        current_words: list[str] = []
        current_start = None
        current_end = None

        for word in words:
            token = normalize_text(word.get("word", ""))
            if not token:
                continue
            token_start = int(word.get("start_ms", 0))
            token_end = int(word.get("end_ms", token_start))
            if current_start is None:
                current_start = token_start
            current_end = token_end
            current_words.append(token)
            current_text = join_tokens(current_words)
            if should_flush(current_text, token, max_chars):
                cues.append(
                    {
                        "index": cue_index,
                        "start_ms": current_start,
                        "end_ms": max(current_end, current_start + 400),
                        "text": current_text,
                        "slide_index": slide.get("slide_index"),
                    }
                )
                cue_index += 1
                current_words = []
                current_start = None
                current_end = None

        if current_words and current_start is not None and current_end is not None:
            cues.append(
                    {
                        "index": cue_index,
                        "start_ms": current_start,
                        "end_ms": max(current_end, current_start + 400),
                        "text": join_tokens(current_words),
                        "slide_index": slide.get("slide_index"),
                    }
                )
            cue_index += 1

    deduped: list[dict] = []
    last_end = -1
    for cue in cues:
        start_ms = max(int(cue["start_ms"]), last_end + 1)
        end_ms = max(int(cue["end_ms"]), start_ms + 300)
        deduped.append({**cue, "start_ms": start_ms, "end_ms": end_ms})
        last_end = end_ms
    return deduped


def render_srt(cues: Iterable[dict]) -> str:
    blocks: list[str] = []
    for cue in cues:
        blocks.append(
            "\n".join(
                [
                    str(cue["index"]),
                    f"{format_timestamp(cue['start_ms'], vtt=False)} --> {format_timestamp(cue['end_ms'], vtt=False)}",
                    cue["text"],
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def render_vtt(cues: Iterable[dict]) -> str:
    blocks = ["WEBVTT\n"]
    for cue in cues:
        blocks.append(
            "\n".join(
                [
                    str(cue["index"]),
                    f"{format_timestamp(cue['start_ms'], vtt=True)} --> {format_timestamp(cue['end_ms'], vtt=True)}",
                    cue["text"],
                    "",
                ]
            )
        )
    return "\n".join(blocks).rstrip() + "\n"


def write_outputs(manifest_path: Path, output_base: Path, max_chars: int) -> tuple[Path, Path]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    cues = build_cues_from_manifest(manifest, max_chars=max_chars)
    srt_path = output_base.with_suffix(".srt")
    vtt_path = output_base.with_suffix(".vtt")
    srt_path.write_text(render_srt(cues), encoding="utf-8")
    vtt_path.write_text(render_vtt(cues), encoding="utf-8")
    return srt_path, vtt_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate subtitle files from a narration manifest.")
    parser.add_argument("manifest", help="Path to narration-manifest.json")
    parser.add_argument("--output-base", help="Output base path without extension")
    parser.add_argument("--max-chars", type=int, default=26, help="Soft cue length threshold")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    output_base = Path(args.output_base).resolve() if args.output_base else manifest_path.with_name("narration")
    srt_path, vtt_path = write_outputs(manifest_path, output_base, args.max_chars)
    print(f"Wrote {srt_path}")
    print(f"Wrote {vtt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
