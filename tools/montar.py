"""Monta index.html a partir de tools/modelo.html e da lista de imagens de tools/processar.py.
Uso: python tools/montar.py"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import processar as P

CAT = {'mandala': 'Mandala', 'pontilhismo': 'Pontilhismo', 'realismo': 'Realismo', 'outros': 'Old school e fine line'}

def obras():
    li = []
    for i, (_c, _k, cat, leg, _d) in enumerate(P.OBRAS):
        n = f'{i + 1:02d}'
        li.append(f'''    <li class="obra" data-cat="{cat}"><button class="obra-btn" data-g="{n}" aria-label="Ampliar: {leg}">
      <img src="assets/img/obras/{n}-p.webp" srcset="assets/img/obras/{n}-p.webp 480w, assets/img/obras/{n}.webp 960w" sizes="(max-width: 700px) 50vw, (max-width: 1100px) 33vw, 25vw" alt="{leg}" width="480" height="600" loading="lazy" decoding="async">
      <span class="obra-leg"><b>{leg}</b><small>{CAT[cat]}</small></span></button></li>''')
    return '\n'.join(li)

def horas():
    li = []
    for i, (_c, _k, h, t, l, _d) in enumerate(P.HORAS):
        li.append(f'''    <li class="peca entra"><figure><img src="assets/img/horas/{i + 1}.webp" alt="{t}: {l}" width="900" height="1125" loading="lazy" decoding="async"></figure>
      <p class="peca-h">{h}</p><h3>{t}</h3><p>{l}</p></li>''')
    return '\n'.join(li)

def trilho(pasta, qtd, alt, w, h):
    return '\n'.join(f'      <li><img src="assets/img/{pasta}/{i + 1:02d}.webp" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async" draggable="false"></li>' for i in range(qtd))

def main():
    s = open(os.path.join(AQUI, 'modelo.html'), encoding='utf-8').read()
    s = s.replace('{{OBRAS}}', obras()).replace('{{HORAS}}', horas())
    s = s.replace('{{CIC}}', trilho('cic', len(P.CIC_HL), 'Tatuagem da Ana cicatrizada, enviada por cliente', 576, 720))
    s = s.replace('{{DISP}}', trilho('disp', len(P.DISP_HL), 'Arte disponível desenhada pela Ana', 576, 720))
    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8', newline='\n').write(s)
    print('index.html ok')

if __name__ == '__main__':
    main()
