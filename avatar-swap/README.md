# avatar-swap

Script de validação: recebe uma **foto de avatar** e um **vídeo**, e devolve o
vídeo com o personagem substituído pelo avatar.

O objetivo aqui não é ser o app — é medir **qualidade e custo reais** antes de
construir backend, fila e frontend em cima.

> Projeto independente do SuportIA. Está nesta pasta só por conveniência;
> quando for pra frente, mova para um repositório próprio.

## Instalação

```bash
pip install -r requirements.txt
cp .env.example .env    # preencha HF_KEY
```

Precisa do **ffmpeg** no PATH (`brew install ffmpeg` / `apt install ffmpeg`).

## Uso

```bash
export HF_KEY="seu-id:seu-secret"       # https://cloud.higgsfield.ai

python swap.py --avatar avatar.png --video viral.mp4 -o saida.mp4
```

Antes de gastar crédito, veja o que seria enviado:

```bash
python swap.py --avatar avatar.png --video viral.mp4 --dry-run
```

## Modos

| Modo | O que faz | Quando usar |
|---|---|---|
| `motion-transfer` (padrão) | O avatar herda movimento, câmera e performance. Cena nova. | Avatar com corpo/estilo próprio |
| `object-swap` | Mantém a cena filmada e troca só a pessoa. | Preservar o cenário do vídeo original |

```bash
python swap.py --avatar a.png --video v.mp4 --mode object-swap
```

## Escolhendo o trecho

Vídeo viral quase nunca é um plano só. O modelo trabalha bem com **um sujeito,
plano estável**, dentro da janela de duração aceita (4–30s no Genjutsu).
Fora disso o resultado degrada — e você paga igual.

```bash
# usa só os 8s a partir do segundo 12
python swap.py --avatar a.png --video v.mp4 --start 12 --duration 8
```

Sem `--duration`, o script corta automaticamente no limite do modelo e avisa.

## Providers

```bash
python swap.py ... --provider higgsfield   # Genjutsu (padrão)
python swap.py ... --provider fal          # Wan 2.2 Animate, precisa de FAL_KEY
```

Custo de referência no Wan via fal: ~US$ 0,08/s em 720p, ~US$ 0,04/s em 480p —
ou seja, **US$ 0,60–1,20 por clipe de 15s**. Orce por clipe, não por mês.

## Quando a API mudar o schema

Os nomes dos parâmetros do Genjutsu não estão fixados neste script por
suposição definitiva. Se a API recusar o job, a mensagem de erro do servidor
é impressa na íntegra — normalmente ela lista os campos esperados. Corrija sem
editar código:

```bash
# troca/adiciona parâmetros (valor é lido como JSON quando possível)
python swap.py ... --arg image_url=https://... --arg resolution=720p --arg seed=42

# aponta para outro endpoint
python swap.py ... --endpoint higgsfield/genjutsu/motion-transfer/v1.1
```

## Flags

| Flag | Para quê |
|---|---|
| `--start` / `--duration` | Recorte do clipe, em segundos |
| `--max-side` | Maior lado em pixels (padrão 1280). Menor = mais barato |
| `--fps` | Força um frame rate |
| `--prompt` | Instrução textual opcional |
| `--arg k=v` | Adiciona/sobrescreve um argumento da API (repetível) |
| `--endpoint` | Sobrescreve o endpoint do modo |
| `--no-prepare` | Pula o ffmpeg e envia os arquivos como estão |
| `--dry-run` | Mostra o payload sem chamar a API |
| `--keep-temp` | Mantém os arquivos intermediários para inspeção |

## Testes

```bash
python test_providers.py
```

## Arquitetura

```
swap.py        CLI e orquestração do pipeline
providers.py   adapters (higgsfield, fal) + extração da URL do resultado
media.py       ffprobe/ffmpeg: análise, recorte, resize
```

`providers.py` é a camada que o backend vai reaproveitar quando isto virar app:
trocar de provider não deve encostar no resto do código.

## Uso responsável

Avatar de personagem próprio é tranquilo. Usar o rosto de uma pessoa real sem
consentimento, ou redistribuir o vídeo original, é onde mora o risco jurídico.
Se isso virar produto, inclua aceite de termos e marcação de conteúdo sintético.
