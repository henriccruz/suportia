"""Inspeção e preparo dos arquivos de entrada via ffmpeg/ffprobe.

Os modelos de troca de personagem são sensíveis à entrada: clipe curto,
um sujeito só, plano estável. Preparar aqui é o que separa um resultado
bom de um borrão caro.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class MediaError(RuntimeError):
    pass


def _require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise MediaError(
            f"{tool} não encontrado no PATH. Instale o ffmpeg "
            "(macOS: brew install ffmpeg | Ubuntu: apt install ffmpeg)."
        )
    return path


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise MediaError(f"{cmd[0]} falhou:\n{result.stderr.strip()}")
    return result.stdout


@dataclass
class VideoInfo:
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool

    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"


def probe_video(path: Path) -> VideoInfo:
    _require("ffprobe")
    raw = _run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-show_streams",
        "-of", "json", str(path),
    ])
    data = json.loads(raw)

    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    if video is None:
        raise MediaError(f"{path} não tem stream de vídeo.")

    # avg_frame_rate vem como "30000/1001"; r_frame_rate é o fallback.
    fps = 0.0
    for key in ("avg_frame_rate", "r_frame_rate"):
        num, _, den = video.get(key, "").partition("/")
        try:
            if float(den or 0) > 0:
                fps = float(num) / float(den)
                break
        except ValueError:
            continue

    duration = float(data.get("format", {}).get("duration") or video.get("duration") or 0)

    return VideoInfo(
        duration=duration,
        width=int(video.get("width", 0)),
        height=int(video.get("height", 0)),
        fps=round(fps, 3),
        has_audio=any(s.get("codec_type") == "audio" for s in streams),
    )


def prepare_video(
    src: Path,
    dst: Path,
    *,
    start: float = 0.0,
    duration: float | None = None,
    max_side: int = 1280,
    fps: float | None = None,
) -> Path:
    """Recorta, redimensiona e normaliza o clipe para o formato que os
    modelos esperam. Mantém a proporção e garante lados pares (libx264)."""
    _require("ffmpeg")

    # force_original_aspect_ratio=decrease só reduz; vídeo menor passa intacto.
    filters = [
        f"scale={max_side}:{max_side}:force_original_aspect_ratio=decrease",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
    ]
    if fps:
        filters.append(f"fps={fps}")

    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", str(src)]
    if duration:
        cmd += ["-t", str(duration)]
    cmd += [
        "-vf", ",".join(filters),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(dst),
    ]
    _run(cmd)
    return dst


def prepare_image(src: Path, dst: Path, *, max_side: int = 1280) -> Path:
    """Normaliza o avatar para JPEG com lado máximo definido."""
    _require("ffmpeg")
    _run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(src),
        "-vf", f"scale={max_side}:{max_side}:force_original_aspect_ratio=decrease",
        "-frames:v", "1", "-q:v", "2",
        str(dst),
    ])
    return dst
