"""Gera og.jpg (1200x630) e apple-touch-icon.png (180x180) a partir do pôster da mandala.
Uso: python tools/og.py"""
import base64, os
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
m = base64.b64encode(open(os.path.join(SITE, 'assets', 'img', 'mandala-a.webp'), 'rb').read()).decode()
FONTES = '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Figtree:wght@500&display=block" rel="stylesheet">'
OG = f'''<html><head>{FONTES}<style>body{{margin:0;width:1200px;height:630px;background:#eee8df;color:#161311;position:relative;overflow:hidden}}
img{{position:absolute;right:-60px;top:-45px;width:720px;height:720px}}
.t{{position:absolute;left:84px;top:150px}} small{{font:500 20px Figtree;letter-spacing:.18em;text-transform:uppercase;color:#6d655d}}
h1{{font:400 132px/0.95 Fraunces;margin:22px 0 26px;letter-spacing:-.02em}} p{{font:500 26px Figtree;margin:0}} i{{color:#c4261d;font-style:normal}}</style></head>
<body><img src="data:image/webp;base64,{m}"><div class="t"><small>Pontilhismo · Curitiba</small><h1>Ana<br>Dias</h1><p>Mandalas feitas ponto a ponto<i>.</i></p></div></body></html>'''
ICO = f'''<html><body style="margin:0;width:180px;height:180px;background:#eee8df"><img src="data:image/webp;base64,{m}" style="width:196px;height:196px;margin:-8px"></body></html>'''
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    pg = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.set_content(OG, wait_until='networkidle'); pg.evaluate('document.fonts.ready')
    pg.screenshot(path=os.path.join(SITE, 'og.jpg'), type='jpeg', quality=86)
    pg = b.new_page(viewport={'width': 180, 'height': 180})
    pg.set_content(ICO); pg.screenshot(path=os.path.join(SITE, 'apple-touch-icon.png'))
    b.close()
print('ok')
