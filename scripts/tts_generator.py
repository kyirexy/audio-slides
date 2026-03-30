#!/usr/bin/env python3
"""Manage Doubao V3 voice clone and narrated slide synthesis."""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from subtitle_helper import write_outputs


VOICE_CLONE_ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/voice_clone"
GET_VOICE_ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/get_voice"
UPGRADE_VOICE_ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/upgrade_voice"
TTS_SSE_ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse"


@dataclass
class SegmentResult:
    slide_index: int
    slide_id: str
    title: str
    text: str
    audio_file: str
    duration_ms: int
    start_ms: int
    end_ms: int
    words: list[dict]


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def get_nested(config: dict, *path: str, default=None):
    value = config
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def require_nested(config: dict, *path: str):
    value = get_nested(config, *path)
    if value in (None, ""):
        raise ValueError(f"Missing required config value: {'.'.join(path)}")
    return value


def new_request_id() -> str:
    return str(uuid.uuid4())


def infer_audio_format(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix in {"wav", "mp3", "ogg", "m4a", "aac", "pcm"}:
        return suffix
    raise ValueError(f"Unsupported audio format: {path.suffix}")


def get_speaker_id(config: dict) -> str:
    return str(require_nested(config, "clone", "speaker_id"))


def get_voice_type(config: dict) -> str:
    voice_type = get_nested(config, "synthesis", "voice_type") or get_nested(config, "clone", "voice_type")
    if voice_type:
        return str(voice_type)
    return get_speaker_id(config)


def validate_common_config(config: dict) -> None:
    if config.get("provider") != "volcengine-doubao-v3":
        raise ValueError(f"Unsupported provider: {config.get('provider')!r}")
    require_nested(config, "credentials", "app_id")
    require_nested(config, "credentials", "access_key")


def build_control_headers(config: dict) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Api-App-Key": str(require_nested(config, "credentials", "app_id")),
        "X-Api-Access-Key": str(require_nested(config, "credentials", "access_key")),
        "X-Api-Request-Id": new_request_id(),
    }


def build_tts_headers(config: dict) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Api-App-Id": str(require_nested(config, "credentials", "app_id")),
        "X-Api-Access-Key": str(require_nested(config, "credentials", "access_key")),
        "X-Api-Resource-Id": str(require_nested(config, "synthesis", "resource_id")),
        "X-Api-Request-Id": new_request_id(),
    }


def post_json(url: str, headers: dict[str, str], payload: dict) -> tuple[dict, dict]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            return json.loads(response_body), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} calling {url}: {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc.reason}") from exc


def build_clone_train_payload(config: dict, audio_path: Path, *, prompt_text: str | None, demo_text: str | None) -> dict:
    clone = config.get("clone", {})
    audio_format = infer_audio_format(audio_path)
    payload = {
        "speaker_id": get_speaker_id(config),
        "audio": {
            "data": base64.b64encode(audio_path.read_bytes()).decode("ascii"),
            "format": audio_format,
        },
    }
    if prompt_text:
        payload["audio"]["text"] = prompt_text
    language = clone.get("language")
    if language is not None:
        payload["language"] = int(language)
    extra_params = dict(clone.get("extra_params") or {})
    if demo_text:
        extra_params["demo_text"] = demo_text
    if extra_params:
        payload["extra_params"] = extra_params
    return payload


def query_voice_status(config: dict) -> tuple[dict, dict]:
    payload = {"speaker_id": get_speaker_id(config)}
    return post_json(GET_VOICE_ENDPOINT, build_control_headers(config), payload)


def ensure_clone_ready(config: dict) -> dict:
    payload, headers = query_voice_status(config)
    status = int(payload.get("status") or 0)
    if status not in {2, 4}:
        raise RuntimeError(
            f"Voice clone is not ready yet. speaker_id={get_speaker_id(config)} status={status}. "
            "Expected 2 (Success) or 4 (Active)."
        )
    logid = headers.get("X-Tt-Logid")
    if logid:
        print(f"Status query logid: {logid}")
    return payload


def build_synthesis_payload(config: dict, text: str) -> dict:
    synthesis = config.get("synthesis", {})
    audio_params = {
        "format": str(synthesis.get("format") or "mp3"),
        "sample_rate": int(synthesis.get("sample_rate") or 24000),
        "speech_rate": int(synthesis.get("speech_rate") or 0),
        "enable_subtitle": bool(synthesis.get("enable_subtitle", True)),
    }
    if synthesis.get("bit_rate") is not None:
        audio_params["bit_rate"] = int(synthesis["bit_rate"])

    req_params = {
        "text": text,
        "speaker": get_voice_type(config),
        "audio_params": audio_params,
    }
    if synthesis.get("model"):
        req_params["model"] = str(synthesis["model"])

    additions = dict(synthesis.get("additions") or {})
    if synthesis.get("silence_duration") is not None:
        additions["silence_duration"] = int(synthesis["silence_duration"])
    if additions:
        req_params["additions"] = json.dumps(additions, ensure_ascii=False)

    return {
        "user": {"uid": str(synthesis.get("uid") or "audio-slides-user")},
        "namespace": str(synthesis.get("namespace") or "BidirectionalTTS"),
        "req_params": req_params,
    }


def parse_sse_response(response) -> tuple[bytearray, list[dict], dict | None]:
    audio_chunks = bytearray()
    sentences: list[dict] = []
    finish_payload = None
    current_event = None
    data_lines: list[str] = []

    def flush_event() -> None:
        nonlocal current_event, data_lines, finish_payload
        if not data_lines:
            current_event = None
            return
        payload = json.loads("\n".join(data_lines))
        code = int(payload.get("code") or 0)
        if code not in {0, 20000000}:
            raise RuntimeError(f"TTS SSE returned code {code}: {payload.get('message') or 'unknown error'}")
        if payload.get("data"):
            audio_chunks.extend(base64.b64decode(payload["data"]))
        if payload.get("sentence"):
            sentences.append(payload["sentence"])
        if code == 20000000:
            finish_payload = payload
        current_event = None
        data_lines = []

    for raw_line in response:
        line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
        if not line:
            flush_event()
            continue
        if line.startswith("event:"):
            current_event = line.partition(":")[2].strip()
            continue
        if line.startswith("data:"):
            data_lines.append(line.partition(":")[2].lstrip())
            continue
        if current_event and data_lines:
            data_lines[-1] += line

    flush_event()
    return audio_chunks, sentences, finish_payload


def synthesize_v3_sse(config: dict, text: str) -> tuple[bytes, list[dict], dict | None, dict]:
    payload = build_synthesis_payload(config, text)
    request = urllib.request.Request(
        TTS_SSE_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=build_tts_headers(config),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            headers = dict(response.headers.items())
            audio_chunks, sentences, finish_payload = parse_sse_response(response)
            return bytes(audio_chunks), sentences, finish_payload, headers
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} calling {TTS_SSE_ENDPOINT}: {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed for {TTS_SSE_ENDPOINT}: {exc.reason}") from exc


def sentence_words_to_manifest(sentences: list[dict], offset_ms: int) -> list[dict]:
    words: list[dict] = []
    for sentence in sentences:
        for item in sentence.get("words", []):
            start_ms = int(round(float(item.get("startTime", 0)) * 1000)) + offset_ms
            end_ms = int(round(float(item.get("endTime", 0)) * 1000)) + offset_ms
            words.append(
                {
                    "word": str(item.get("word", "")),
                    "start_ms": start_ms,
                    "end_ms": max(end_ms, start_ms + 1),
                }
            )
    return words


def estimate_duration_ms(sentences: list[dict]) -> int:
    end_ms = 0
    for sentence in sentences:
        for item in sentence.get("words", []):
            end_ms = max(end_ms, int(round(float(item.get("endTime", 0)) * 1000)))
    return end_ms


def synthesize_segment(config: dict, slide: dict, output_dir: Path, *, offset_ms: int) -> SegmentResult:
    slide_index = int(slide.get("slide_index") or 0)
    slide_id = str(slide.get("slide_id") or f"slide-{slide_index:02d}")
    title = str(slide.get("title") or f"Slide {slide_index}")
    text = " ".join(str(slide.get("narration") or "").split())
    if not text:
        raise ValueError(f"Slide {slide_index} is missing narration text")

    audio_bytes, sentences, finish_payload, headers = synthesize_v3_sse(config, text)
    audio_format = str(get_nested(config, "synthesis", "format", default="mp3"))
    audio_file = f"{slide_id}.{audio_format}"
    (output_dir / audio_file).write_bytes(audio_bytes)
    logid = headers.get("X-Tt-Logid")
    if logid:
        print(f"Synthesized slide {slide_index} logid: {logid}")
    if finish_payload and finish_payload.get("usage"):
        print(f"Slide {slide_index} usage: {json.dumps(finish_payload['usage'], ensure_ascii=False)}")

    duration_ms = estimate_duration_ms(sentences)
    start_ms = offset_ms
    end_ms = offset_ms + duration_ms
    words = sentence_words_to_manifest(sentences, offset_ms)
    return SegmentResult(slide_index, slide_id, title, text, audio_file, duration_ms, start_ms, end_ms, words)


def write_manifest(output_dir: Path, config: dict, results: list[SegmentResult], *, combined_audio: str | None) -> Path:
    manifest = {
        "provider": config["provider"],
        "resource_id": get_nested(config, "synthesis", "resource_id"),
        "voice_type": get_voice_type(config),
        "generated_at": datetime.now(UTC).isoformat(),
        "audio_encoding": str(get_nested(config, "synthesis", "format", default="mp3")),
        "combined_audio": combined_audio,
        "slides": [
            {
                "slide_index": item.slide_index,
                "slide_id": item.slide_id,
                "title": item.title,
                "text": item.text,
                "audio_file": item.audio_file,
                "duration_ms": item.duration_ms,
                "start_ms": item.start_ms,
                "end_ms": item.end_ms,
                "words": item.words,
            }
            for item in results
        ],
    }
    manifest_path = output_dir / "narration-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def maybe_combine_audio(output_dir: Path, results: list[SegmentResult]) -> str | None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg or not results:
        return None

    concat_path = output_dir / "concat.txt"
    combined_name = f"narration-full{Path(results[0].audio_file).suffix}"
    concat_path.write_text("\n".join(f"file '{item.audio_file}'" for item in results) + "\n", encoding="utf-8")
    completed = subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", concat_path.name, "-c", "copy", combined_name],
        cwd=output_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    return combined_name if completed.returncode == 0 else None


def command_clone_train(args: argparse.Namespace) -> int:
    config = load_json(args.config)
    validate_common_config(config)
    audio_path = Path(args.audio).resolve()
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    payload = build_clone_train_payload(config, audio_path, prompt_text=args.prompt_text, demo_text=args.demo_text)
    response, headers = post_json(VOICE_CLONE_ENDPOINT, build_control_headers(config), payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    if headers.get("X-Tt-Logid"):
        print(f"logid: {headers['X-Tt-Logid']}")
    return 0


def command_clone_status(args: argparse.Namespace) -> int:
    config = load_json(args.config)
    validate_common_config(config)
    response, headers = query_voice_status(config)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    if headers.get("X-Tt-Logid"):
        print(f"logid: {headers['X-Tt-Logid']}")
    return 0


def command_clone_upgrade(args: argparse.Namespace) -> int:
    config = load_json(args.config)
    validate_common_config(config)
    payload = {"speaker_id": get_speaker_id(config)}
    response, headers = post_json(UPGRADE_VOICE_ENDPOINT, build_control_headers(config), payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    if headers.get("X-Tt-Logid"):
        print(f"logid: {headers['X-Tt-Logid']}")
    return 0


def command_probe(args: argparse.Namespace) -> int:
    config = load_json(args.config)
    validate_common_config(config)
    if not args.skip_status_check:
        status_payload = ensure_clone_ready(config)
        print(f"Clone status OK: {status_payload.get('status')} for speaker_id={get_speaker_id(config)}")

    output_dir = Path(args.output_dir or Path(args.config).resolve().parent / "probe-output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_bytes, sentences, finish_payload, headers = synthesize_v3_sse(config, args.text)
    audio_format = str(get_nested(config, "synthesis", "format", default="mp3"))
    audio_path = output_dir / f"probe.{audio_format}"
    audio_path.write_bytes(audio_bytes)
    manifest = {
        "provider": config["provider"],
        "resource_id": get_nested(config, "synthesis", "resource_id"),
        "voice_type": get_voice_type(config),
        "generated_at": datetime.now(UTC).isoformat(),
        "slides": [
            {
                "slide_index": 1,
                "slide_id": "probe",
                "title": "Probe",
                "text": args.text,
                "audio_file": audio_path.name,
                "duration_ms": estimate_duration_ms(sentences),
                "start_ms": 0,
                "end_ms": estimate_duration_ms(sentences),
                "words": sentence_words_to_manifest(sentences, 0),
            }
        ],
    }
    manifest_path = output_dir / "probe-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_outputs(manifest_path, output_dir / "probe", max_chars=args.max_chars)
    print(f"Wrote probe audio: {audio_path}")
    print(f"Wrote probe manifest: {manifest_path}")
    if headers.get("X-Tt-Logid"):
        print(f"logid: {headers['X-Tt-Logid']}")
    if finish_payload and finish_payload.get("usage"):
        print(f"usage: {json.dumps(finish_payload['usage'], ensure_ascii=False)}")
    return 0


def command_synthesize(args: argparse.Namespace) -> int:
    config = load_json(args.config)
    validate_common_config(config)
    ensure_clone_ready(config)
    plan = load_json(args.script)
    slides = plan.get("slides") or []
    if not slides:
        raise ValueError("Narration plan is missing slides")

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[SegmentResult] = []
    offset_ms = 0
    for slide in slides:
        result = synthesize_segment(config, slide, output_dir, offset_ms=offset_ms)
        results.append(result)
        offset_ms = result.end_ms
        print(f"Synthesized slide {result.slide_index}: {result.audio_file}")

    combined_audio = maybe_combine_audio(output_dir, results)
    manifest_path = write_manifest(output_dir, config, results, combined_audio=combined_audio)
    write_outputs(manifest_path, output_dir / "narration", max_chars=args.max_chars)
    print(f"Wrote manifest: {manifest_path}")
    if combined_audio:
        print(f"Wrote combined audio: {output_dir / combined_audio}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Doubao V3 voice clone and narrated slide synthesis.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    clone_train = subparsers.add_parser("clone-train", help="Upload a training sample to the V3 voice clone endpoint")
    clone_train.add_argument("--config", required=True, help="Path to provider config JSON")
    clone_train.add_argument("--audio", required=True, help="Path to a training audio sample")
    clone_train.add_argument("--prompt-text", help="Optional transcript of the prompt audio")
    clone_train.add_argument("--demo-text", help="Optional demo text for the training response")
    clone_train.set_defaults(func=command_clone_train)

    clone_status = subparsers.add_parser("clone-status", help="Query V3 voice clone status")
    clone_status.add_argument("--config", required=True, help="Path to provider config JSON")
    clone_status.set_defaults(func=command_clone_status)

    clone_upgrade = subparsers.add_parser("clone-upgrade", help="Upgrade a voice clone to unified voice management")
    clone_upgrade.add_argument("--config", required=True, help="Path to provider config JSON")
    clone_upgrade.set_defaults(func=command_clone_upgrade)

    probe = subparsers.add_parser("probe", help="Run a live V3 synthesis probe")
    probe.add_argument("--config", required=True, help="Path to provider config JSON")
    probe.add_argument("--text", required=True, help="Probe text")
    probe.add_argument("--output-dir", help="Directory for the probe output")
    probe.add_argument("--skip-status-check", action="store_true", help="Skip the clone status check")
    probe.add_argument("--max-chars", type=int, default=26, help="Soft subtitle cue length threshold")
    probe.set_defaults(func=command_probe)

    synthesize = subparsers.add_parser("synthesize", help="Generate narration assets from a narration plan")
    synthesize.add_argument("--config", required=True, help="Path to provider config JSON")
    synthesize.add_argument("--script", required=True, help="Path to narration plan JSON")
    synthesize.add_argument("--output-dir", required=True, help="Output directory")
    synthesize.add_argument("--max-chars", type=int, default=26, help="Soft subtitle cue length threshold")
    synthesize.set_defaults(func=command_synthesize)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
