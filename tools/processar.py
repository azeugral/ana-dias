"""Gera as imagens do site a partir de _ref/ig (posts) e _ref/hl (destaques).
Uso: python tools/processar.py   (--folha só monta _ref/conf-portfolio.jpg para conferir os recortes)"""
import glob, json, os, sys
from PIL import Image, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
R = os.path.join(SITE, '..', '_ref'); A = os.path.join(SITE, 'assets', 'img')

# (post, foto, categoria, legenda, desvio vertical do recorte 0..1)
OBRAS = [
    ('004', 1, 'mandala', 'Mandala no antebraço', .5),
    ('071', 1, 'mandala', 'Mandala no antebraço, milhares de pontos', .45),
    ('080', 1, 'mandala', 'Ombro, início de fechamento', .4),
    ('124', 1, 'mandala', 'Pescoço, sessão única', .45),
    ('043', 1, 'mandala', 'Mão inteira', .5),
    ('016', 1, 'mandala', 'Mandala na nuca e pescoço', .4),
    ('097', 1, 'mandala', 'Cotovelo com linhas', .5),
    ('093', 2, 'mandala', 'Mandala com vermelho', .5),
    ('091', 1, 'mandala', 'Ombro, pétalas abertas', .45),
    ('106', 1, 'mandala', 'Início de um projeto de costas', .45),
    ('147', 1, 'mandala', 'Pescoço em pontilhismo', .45),
    ('089', 1, 'mandala', 'Nuca', .5),
    ('022', 1, 'mandala', 'Dorso da mão', .5),
    ('007', 1, 'mandala', 'Joelho, três sessões', .5),
    ('042', 1, 'mandala', 'Par nos cotovelos', .5),
    ('029', 2, 'mandala', 'Mandala com sombra', .45),
    ('078', 1, 'pontilhismo', 'Retrato e rosas no braço', .45),
    ('117', 1, 'pontilhismo', 'Tigre e lua', .4),
    ('123', 2, 'pontilhismo', 'Underboob exclusivo', .5),
    ('027', 2, 'pontilhismo', 'Braço fechado com mandalas', .45),
    ('096', 1, 'pontilhismo', 'Retrato 100% em pontos', .45),
    ('095', 1, 'pontilhismo', 'E.T., só pontos', .45),
    ('009', 1, 'realismo', 'Kali em preto e cinza', .4),
    ('018', 2, 'realismo', 'Olho de tigre', .5),
    ('050', 1, 'realismo', 'Caveira em preto e cinza', .5),
    ('041', 1, 'realismo', 'Lobo e retrato', .45),
    ('057', 1, 'realismo', 'Coruja de 7 cm', .5),
    ('046', 1, 'realismo', 'Estudo de realismo', .5),
    ('075', 1, 'outros', 'Fechamento old school colorido', .45),
    ('085', 1, 'outros', 'The Lovers, tarô exclusivo', .5),
    ('102', 1, 'outros', 'Pantera old school', .5),
    ('032', 1, 'outros', 'Águia no pescoço, 2h20', .45),
    ('037', 3, 'outros', 'Fine line', .5),
]
# peças grandes: (post, foto, horas, título, linha, desvio)
HORAS = [
    ('112', 1, '20 h', 'Art Tattoo Expo Sul', 'Perna inteira em pontos, feita no estande da convenção.', .5),
    ('023', 1, '35 h', 'Sete sessões', 'Antebraço fechado com mandala, geometria e degradê.', .45),
    ('128', 1, '15 h', 'Costas em dois dias', 'Mandala, retrato e tigre fundidos no mesmo desenho.', .4),
    ('120', 1, '11 h', 'Tattoo Week', 'Retrato com mandala para a maior convenção do Brasil.', .4),
    ('137', 1, '★', 'Premiada', 'Peça premiada na categoria pontilhismo.', .5),
]
SOBRE = [('038', 6, .85), ('038', 2, .4)]
# recém-feita x cicatrizada (posts) e quadros do destaque Cicatrizadinhas
CIC_POSTS = [('068', 1, .45), ('068', 2, .45)]
CIC_HL = [17, 21, 24, 25, 26, 29, 31, 32, 30, 2, 11, 38]
DISP_HL = [2, 3, 4, 5, 7, 8, 9, 10, 11, 12]   # a 6 mostra preço antigo (R$ 6.000), fica de fora

def post(cod, k):
    return glob.glob(os.path.join(R, 'ig', f'{cod}_*_{k}*.jpg'))[0]

def recortar(src, w, h, dy=.5):
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(.5, dy))

def salvar(im, nome, q=82):
    os.makedirs(os.path.dirname(os.path.join(A, nome)), exist_ok=True)
    im.save(os.path.join(A, nome), 'WEBP', quality=q, method=6)

def main():
    if '--folha' in sys.argv:
        ims = [recortar(post(c, k), 240, 300, dy) for c, k, *_r, dy in OBRAS] + [recortar(post(c, k), 240, 300, dy) for c, k, _h, _t, _l, dy in HORAS]
        folha = Image.new('RGB', (240 * 8, 300 * ((len(ims) + 7) // 8)), 'white')
        for i, im in enumerate(ims): folha.paste(im, ((i % 8) * 240, (i // 8) * 300))
        folha.save(os.path.join(R, 'conf-portfolio.jpg'), quality=80); return
    dados = {'obras': [], 'horas': []}
    for i, (c, k, cat, leg, dy) in enumerate(OBRAS):
        im = recortar(post(c, k), 960, 1200, dy)
        salvar(im, f'obras/{i + 1:02d}.webp'); salvar(im.resize((480, 600), Image.LANCZOS), f'obras/{i + 1:02d}-p.webp', 78)
        dados['obras'].append({'n': i + 1, 'cat': cat, 'leg': leg})
    for i, (c, k, h, t, l, dy) in enumerate(HORAS):
        salvar(recortar(post(c, k), 900, 1125, dy), f'horas/{i + 1}.webp')
        dados['horas'].append({'h': h, 't': t, 'l': l})
    for i, (c, k, dy) in enumerate(SOBRE):
        salvar(recortar(post(c, k), 1000, 1250, dy), f'sobre-{i + 1}.webp', 84)
    for i, (c, k, dy) in enumerate(CIC_POSTS):
        salvar(recortar(post(c, k), 800, 1000, dy), f'cic/post-{i + 1}.webp')
    for i, n in enumerate(CIC_HL):
        salvar(recortar(os.path.join(R, 'hl', f'cic_{n:02d}.jpg'), 360, 640), f'cic/{i + 1:02d}.webp', 80)
    for i, n in enumerate(DISP_HL):
        salvar(recortar(os.path.join(R, 'hl', f'disponiveis_{n:02d}.jpg'), 640, 1138), f'disp/{i + 1:02d}.webp', 80)
    json.dump(dados, open(os.path.join(R, 'imagens.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('ok', len(OBRAS), 'obras')

if __name__ == '__main__':
    main()
