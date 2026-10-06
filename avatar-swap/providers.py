"""Adapters dos providers de troca de personagem.

Cada provider sabe três coisas: subir um arquivo e devolver URL pública,
submeter o job, e acompanhar até terminar. O resto do app não precisa
saber de qual provider veio o vídeo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

StatusCallback = Callable[[str], None]


class ProviderError(RuntimeError):
    pass


# Extensões que consideramos vídeo ao vasculhar a resposta do provider.
_VIDEO_SUFFIXES = (".mp4", ".mov", ".webm", ".m4v")
# Mídia que nunca é o resultado: thumbnails, preview de frame, áudio extraído.
_NOT_VIDEO_SUFFIXES = (
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".bmp",
    ".mp3", ".wav", ".m4a", ".ogg", ".json", ".txt",
)


def find_video_url(payload: Any) -> str | None:
    """Varre a resposta atrás da URL do vídeo.

    Os providers divergem no formato (``video.url``, ``videos[0].url``,
    ``output``, ``results[].url``...). Em vez de fixar um caminho, procura
    recursivamente a primeira string que pareça URL de vídeo. Chaves com
    nome de vídeo têm prioridade sobre as demais.
    """
    def walk(node: Any, prefer: bool) -> Iterable[tuple[bool, str]]:
        if isinstance(node, str):
            low = node.lower()
            if low.startswith(("http://", "https://")):
                path = low.split("?")[0]
                if path.endswith(_NOT_VIDEO_SUFFIXES):
                    return
                is_video = path.endswith(_VIDEO_SUFFIXES)
                if is_video or prefer:
                    yield (is_video, node)
        elif isinstance(node, dict):
            for key, value in node.items():
                key_hints = any(h in key.lower() for h in ("video", "output", "result", "url"))
                yield from walk(value, prefer or key_hints)
        elif isinstance(node, (list, tuple)):
            for item in node:
                yield from walk(item, prefer)

    matches = list(walk(payload, False))
    if not matches:
        return None
    # Uma URL com extensão de vídeo ganha de uma que só estava sob chave sugestiva.
    matches.sort(key=lambda m: not m[0])
    return matches[0][1]


@dataclass
class Job:
    """Resultado bruto de uma execução, já com a URL do vídeo resolvida."""
    provider: str
    request_id: str | None
    raw: Any
    video_url: str | None = field(default=None)

    def __post_init__(self) -> None:
        if self.video_url is None:
            self.video_url = find_video_url(self.raw)


class Provider:
    name = "base"
    default_endpoint = ""
    # Janela de duração aceita pelo modelo, em segundos.
    duration_range = (3.0, 15.0)

    def check_credentials(self) -> None:
        """Falha cedo, antes de gastar tempo preparando os arquivos."""
        raise NotImplementedError

    def upload_file(self, path: Path) -> str:
        raise NotImplementedError

    def build_args(self, image_url: str, video_url: str, prompt: str | None) -> dict[str, Any]:
        raise NotImplementedError

    def run(self, endpoint: str, args: dict[str, Any], on_status: StatusCallback) -> Job:
        raise NotImplementedError


class HiggsfieldProvider(Provider):
    """Genjutsu, da Higgsfield. Usa o SDK oficial (``higgsfield-client``).

    Credenciais: HF_KEY="id:secret", ou HF_API_KEY + HF_API_SECRET.
    """

    name = "higgsfield"
    # Confirmado publicamente: POST /higgsfield/genjutsu/motion-transfer/v1.0
    default_endpoint = "higgsfield/genjutsu/motion-transfer/v1.0"
    duration_range = (4.0, 30.0)

    # Endpoints por modo. Só motion-transfer está confirmado; object-swap é
    # palpite derivado do nome do modo no produto — sobrescreva com --endpoint
    # se a API recusar.
    endpoints = {
        "motion-transfer": "higgsfield/genjutsu/motion-transfer/v1.0",
        "object-swap": "higgsfield/genjutsu/object-swap/v1.0",
    }

    def __init__(self) -> None:
        try:
            import higgsfield_client  # noqa: PLC0415
        except ImportError as exc:
            raise ProviderError(
                "SDK ausente. Rode: pip install higgsfield-client"
            ) from exc
        self._hf = higgsfield_client

    def check_credentials(self) -> None:
        if os.getenv("HF_KEY"):
            return
        if os.getenv("HF_API_KEY") and os.getenv("HF_API_SECRET"):
            return
        raise ProviderError(
            'Credencial ausente. Defina HF_KEY="id:secret" (ou HF_API_KEY + '
            "HF_API_SECRET). Pegue as suas em https://cloud.higgsfield.ai"
        )

    def upload_file(self, path: Path) -> str:
        return self._hf.upload_file(path)

    def build_args(self, image_url: str, video_url: str, prompt: str | None) -> dict[str, Any]:
        args: dict[str, Any] = {
            "input_image_url": image_url,
            "input_video_url": video_url,
        }
        if prompt:
            args["prompt"] = prompt
        return args

    def run(self, endpoint: str, args: dict[str, Any], on_status: StatusCallback) -> Job:
        from higgsfield_client.exceptions import HiggsfieldClientError  # noqa: PLC0415

        try:
            controller = self._hf.submit(endpoint, arguments=args)
        except HiggsfieldClientError as exc:
            # A mensagem do servidor costuma listar os campos esperados —
            # é o que resolve um erro de nome de parâmetro.
            raise ProviderError(f"Higgsfield recusou o job: {exc}") from exc

        on_status(f"job enviado (request_id={controller.request_id})")
        seen = None
        for status in controller.poll_request_status(delay=3.0):
            label = type(status).__name__
            if label != seen:
                on_status(label)
                seen = label

        result = controller.get()
        status = (result or {}).get("status")
        if status and status not in ("completed",):
            raise ProviderError(f"Job terminou como '{status}': {result}")

        return Job(provider=self.name, request_id=controller.request_id, raw=result)


class FalProvider(Provider):
    """Wan 2.2 Animate (modo replace), via fal.ai. Credencial: FAL_KEY."""

    name = "fal"
    default_endpoint = "fal-ai/wan/v2.2-14b/animate/replace"
    duration_range = (3.0, 15.0)

    endpoints = {
        "object-swap": "fal-ai/wan/v2.2-14b/animate/replace",
        "motion-transfer": "fal-ai/wan/v2.2-14b/animate/move",
    }

    def __init__(self) -> None:
        try:
            import fal_client  # noqa: PLC0415
        except ImportError as exc:
            raise ProviderError("SDK ausente. Rode: pip install fal-client") from exc
        self._fal = fal_client

    def check_credentials(self) -> None:
        if not os.getenv("FAL_KEY"):
            raise ProviderError(
                "Credencial ausente. Defina FAL_KEY. Pegue a sua em "
                "https://fal.ai/dashboard/keys"
            )

    def upload_file(self, path: Path) -> str:
        return self._fal.upload_file(str(path))

    def build_args(self, image_url: str, video_url: str, prompt: str | None) -> dict[str, Any]:
        args: dict[str, Any] = {"image_url": image_url, "video_url": video_url}
        if prompt:
            args["prompt"] = prompt
        return args

    def run(self, endpoint: str, args: dict[str, Any], on_status: StatusCallback) -> Job:
        handle = self._fal.submit(endpoint, arguments=args)
        on_status(f"job enviado (request_id={handle.request_id})")

        seen = None
        for event in handle.iter_events(with_logs=False):
            label = type(event).__name__
            if label != seen:
                on_status(label)
                seen = label

        return Job(provider=self.name, request_id=handle.request_id, raw=handle.get())


PROVIDERS: dict[str, type[Provider]] = {
    "higgsfield": HiggsfieldProvider,
    "fal": FalProvider,
}


def get_provider(name: str) -> Provider:
    try:
        return PROVIDERS[name]()
    except KeyError:
        raise ProviderError(
            f"Provider '{name}' desconhecido. Opções: {', '.join(PROVIDERS)}"
        ) from None
