"""Testes do parsing de resposta. Rode com: python3 test_providers.py"""

import sys

from providers import find_video_url

CASES = [
    ("video.url (fal)",        {"video": {"url": "https://cdn/out.mp4"}}, "https://cdn/out.mp4"),
    ("lista videos[]",         {"videos": [{"url": "https://cdn/a.mp4"}]}, "https://cdn/a.mp4"),
    ("results[] com thumb",    {"results": [{"thumbnail": "https://cdn/t.jpg",
                                             "url": "https://cdn/b.mov"}]}, "https://cdn/b.mov"),
    ("output como string",     {"output": "https://cdn/c.webm"}, "https://cdn/c.webm"),
    ("url assinada",           {"video_url": "https://cdn/d.mp4?sig=abc"}, "https://cdn/d.mp4?sig=abc"),
    ("aninhado em results",    {"status": "completed",
                                "results": {"raw": {"url": "https://cdn/e.mp4"}}}, "https://cdn/e.mp4"),
    ("sem extensão, sob url",  {"result": {"url": "https://cdn/signed/zzz"}}, "https://cdn/signed/zzz"),
    ("resposta vazia",         {"status": "completed"}, None),
    ("só imagem",              {"images": [{"url": "https://cdn/x.png"}]}, None),
    ("thumb antes do vídeo",   {"output": {"thumb_url": "https://cdn/t.webp",
                                           "video": "https://cdn/f.mp4"}}, "https://cdn/f.mp4"),
    ("áudio junto",            {"result": {"audio_url": "https://cdn/a.wav",
                                           "video_url": "https://cdn/g.mp4"}}, "https://cdn/g.mp4"),
]


def main() -> int:
    failures = 0
    for name, payload, expected in CASES:
        got = find_video_url(payload)
        if got == expected:
            print(f"ok     {name}")
        else:
            failures += 1
            print(f"FALHOU {name}: esperava {expected!r}, veio {got!r}")

    print(f"\n{len(CASES) - failures}/{len(CASES)} passaram")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
