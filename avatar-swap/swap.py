#!/usr/bin/env python3
"""Troca o personagem de um vídeo pelo avatar de uma foto.

Script de validação: roda o pipeline inteiro (preparo -> upload -> geração
-> download) numa chamada só, pra medir qualidade e custo antes de
construir app em cima.

    python swap.py --avatar avatar.png --video viral.mp4 -o saida.mp4
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import media
import providers

try:  # httpx chega junto com os SDKs dos providers
    import httpx
    NETWORK_ERRORS: tuple[type[BaseException], ...] = (
        httpx.HTTPError, urllib.error.URLError, OSError,
    )
except ImportError:
    NETWORK_ERRORS = (urllib.error.URLError, OSError)


def log(msg: str) -> None:
    print(f"  {msg}", flush=True)


def step(msg: str) -> None:
    print(f"\n▸ {msg}", flush=True)


def parse_overrides(pairs: list[str]) -> dict[str, object]:
    """--arg chave=valor, com o valor interpretado como JSON quando possível.

    Permite corrigir o nome ou o tipo de um parâmetro sem editar o código,
    que é o que se faz quando a API muda o schema.
    """
    out: dict[str, object] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise SystemExit(f"--arg precisa do formato chave=valor (recebi '{pair}')")
        try:
            out[key] = json.loads(value)
        except json.JSONDecodeError:
            out[key] = value
    return out


def download(url: str, dst: Path) -> Path:
    with urllib.request.urlopen(url) as response, open(dst, "wb") as fh:
        shutil.copyfileobj(response, fh)
    return dst


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Substitui o personagem de um vídeo pelo avatar de uma foto.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--avatar", required=True, type=Path, help="Foto do avatar")
    parser.add_argument("--video", required=True, type=Path, help="Vídeo de referência")
    parser.add_argument("-o", "--out", type=Path, default=Path("saida.mp4"),
                        help="Arquivo de saída")

    parser.add_argument("--provider", default="higgsfield",
                        choices=sorted(providers.PROVIDERS), help="Provider de geração")
    parser.add_argument("--mode", default="motion-transfer",
                        choices=["motion-transfer", "object-swap"],
                        help="motion-transfer: avatar herda o movimento. "
                             "object-swap: mantém a cena e troca só a pessoa")
    parser.add_argument("--endpoint", help="Sobrescreve o endpoint do modo")
    parser.add_argument("--prompt", help="Instrução textual opcional")
    parser.add_argument("--arg", action="append", default=[], metavar="CHAVE=VALOR",
                        help="Adiciona/sobrescreve um argumento enviado à API")

    parser.add_argument("--start", type=float, default=0.0,
                        help="Segundo inicial do recorte")
    parser.add_argument("--duration", type=float,
                        help="Duração do recorte (padrão: limite do modelo)")
    parser.add_argument("--max-side", type=int, default=1280,
                        help="Maior lado do vídeo e da imagem, em pixels")
    parser.add_argument("--fps", type=float, help="Força um frame rate")

    parser.add_argument("--no-prepare", action="store_true",
                        help="Envia os arquivos como estão, sem passar pelo ffmpeg")
    parser.add_argument("--dry-run", action="store_true",
                        help="Prepara e mostra o payload, mas não chama a API")
    parser.add_argument("--keep-temp", action="store_true",
                        help="Mantém os arquivos intermediários")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    for path in (args.avatar, args.video):
        if not path.is_file():
            print(f"erro: arquivo não encontrado: {path}", file=sys.stderr)
            return 1

    try:
        provider = providers.get_provider(args.provider)
    except providers.ProviderError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    # Dry-run não chama a API, então não exige credencial.
    if not args.dry_run:
        try:
            provider.check_credentials()
        except providers.ProviderError as exc:
            print(f"erro: {exc}", file=sys.stderr)
            return 1

    endpoint = args.endpoint or provider.endpoints.get(args.mode, provider.default_endpoint)
    min_dur, max_dur = provider.duration_range

    step("Analisando o vídeo")
    try:
        info = media.probe_video(args.video)
    except media.MediaError as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1

    log(f"{info.resolution} · {info.fps} fps · {info.duration:.1f}s "
        f"· áudio: {'sim' if info.has_audio else 'não'}")

    clip_duration = args.duration or min(info.duration - args.start, max_dur)
    if clip_duration < min_dur:
        log(f"⚠ trecho de {clip_duration:.1f}s é menor que o mínimo de {min_dur:.0f}s "
            "do modelo; o provider pode recusar")
    if info.duration > max_dur and not args.duration:
        log(f"⚠ vídeo tem {info.duration:.1f}s e o modelo aceita até {max_dur:.0f}s; "
            f"cortando em {args.start:.1f}s–{args.start + clip_duration:.1f}s "
            "(use --start/--duration para escolher outro trecho)")

    workdir = Path(tempfile.mkdtemp(prefix="avatar-swap-"))
    try:
        if args.no_prepare:
            avatar_path, video_path = args.avatar, args.video
        else:
            step("Preparando os arquivos")
            avatar_path = media.prepare_image(
                args.avatar, workdir / "avatar.jpg", max_side=args.max_side
            )
            video_path = media.prepare_video(
                args.video, workdir / "clip.mp4",
                start=args.start, duration=clip_duration,
                max_side=args.max_side, fps=args.fps,
            )
            log(f"avatar: {avatar_path.stat().st_size / 1024:.0f} KB · "
                f"clipe: {video_path.stat().st_size / 1024 / 1024:.1f} MB")

        step(f"Enviando para {provider.name} · {endpoint}")
        if args.dry_run:
            payload = provider.build_args("<avatar-url>", "<video-url>", args.prompt)
            payload.update(parse_overrides(args.arg))
            log("dry-run, nada foi enviado. Payload:")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return 0

        avatar_url = provider.upload_file(avatar_path)
        video_url = provider.upload_file(video_path)
        log("upload concluído")

        payload = provider.build_args(avatar_url, video_url, args.prompt)
        payload.update(parse_overrides(args.arg))

        started = time.monotonic()
        job = provider.run(endpoint, payload, on_status=log)
        elapsed = time.monotonic() - started

        if not job.video_url:
            print("\nerro: o provider respondeu, mas não achei a URL do vídeo. "
                  "Resposta completa:", file=sys.stderr)
            print(json.dumps(job.raw, indent=2, ensure_ascii=False), file=sys.stderr)
            return 1

        step("Baixando o resultado")
        download(job.video_url, args.out)
        log(f"{args.out} · {args.out.stat().st_size / 1024 / 1024:.1f} MB "
            f"· {elapsed / 60:.1f} min de geração")
        return 0

    except providers.ProviderError as exc:
        print(f"\nerro: {exc}", file=sys.stderr)
        return 1
    except media.MediaError as exc:
        print(f"\nerro: {exc}", file=sys.stderr)
        return 1
    except NETWORK_ERRORS as exc:
        print(f"\nerro de rede ao falar com {provider.name}: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        print("Verifique a conexão, o proxy e se a credencial está no ambiente.",
              file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrompido", file=sys.stderr)
        return 130
    finally:
        if args.keep_temp:
            print(f"\narquivos intermediários em {workdir}")
        else:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
