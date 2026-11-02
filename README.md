# Ana Dias · Pontilhismo em Curitiba

Prévia de site feita pelo LRGZ para a Ana Dias ([@anadiastattoo](https://instagram.com/anadiastattoo)), especialista em pontilhismo que atende no estúdio Traço Nobre ([@traconobretattoo](https://instagram.com/traconobretattoo)).

Endereço da prévia: https://azeugral.github.io/ana-dias/ (com `noindex` e `robots.txt` bloqueando tudo até ela aprovar).

## Como está montado

- **Hero:** 26.000 pontos que formam, ponto a ponto, duas mandalas disponíveis da Ana e trocam entre elas. No desktop roda em WebGL (`assets/js/pontos.js` + `assets/pontos.bin`). No celular e no tablet entra o vídeo `assets/video/mandala.mp4`. Com movimento reduzido fica o pôster parado.
- **Seções:** sobre, trabalhos (filtro + ver mais), peças de muitas horas, cicatrizadas, disponíveis, feedbacks, como funciona, estúdio Traço Nobre e chamada final.
- **Contato:** todos os botões vão para a DM (`https://ig.me/m/anadiastattoo`).

## Ferramentas (`tools/`)

| Arquivo | Faz |
|---|---|
| `mandalas.py` | Pontilha as mandalas e grava `assets/pontos.bin` |
| `gerar_video.py` | Pôsteres `mandala-a/b.webp` e o MP4 do hero |
| `processar.py` | Recorta as fotos do Instagram e dos destaques |
| `modelo.html` + `montar.py` | Monta o `index.html` (editar o modelo, nunca o index) |
| `og.py` | `og.jpg` e `apple-touch-icon.png` |

O material bruto (posts, destaques, folhas de contato) fica fora do repo, em `../_ref/`.

## CONFIRMAR antes de publicar de verdade

1. **WhatsApp:** o número (41) 98810-5984 aparece nas legendas de 2022 a 2024, mas a bio de hoje não tem link. Por enquanto o site só leva para a DM.
2. **Tempo de carreira:** o site diz 9 anos (em abril de 2025 ela escreveu 8).
3. **Prêmio:** de qual convenção e de que ano é a peça premiada (post 137).
4. **Feedbacks:** os textos foram transcritos dos prints dos destaques. Confirmar se pode usar os nomes (Bárbara, Gabrielle) ou deixar como "Cliente".
5. **Traço Nobre:** confirmar que o estúdio tem bar próprio e manter o endereço Rua Lúcio Rasera, 175, Bigorrilho.
6. **Disponíveis:** conferir quais desenhos ainda estão livres (o de R$ 6.000 ficou de fora porque mostrava preço).
7. **Fotos de clientes:** as cicatrizadas vieram dos destaques. Confirmar se pode exibir.
8. **Domínio:** a definir. Ao trocar, ajustar `og:image` no `tools/modelo.html` e tirar o `noindex` e o `robots.txt`.
9. **Cache:** CSS e JS usam `?v=1`. Ao mudar, subir o número no modelo.

---

Site por L R G Z
