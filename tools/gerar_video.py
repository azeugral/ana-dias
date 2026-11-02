"""Renderiza o hero de pontos (assets/js/pontos.js) num Edge headless:
- assets/video/mandala.mp4: laço sem emenda A -> B -> A (720x720, crf 33 ≈ 4,7 MB; celular e tablet);
- assets/img/mandala-a.webp e mandala-b.webp: pôsteres e a mandala da chamada final.
O fundo é o papel do site, igual ao do CSS, e a borda some numa máscara radial no CSS.
Uso: python tools/gerar_video.py [--teste]   (--teste só grava quadros em _ref/hero/quadro-*.png)"""
import base64, io, os, subprocess, sys
from playwright.sync_api import sync_playwright
import imageio_ffmpeg
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
VID = os.path.join(SITE, 'assets', 'video'); IMG = os.path.join(SITE, 'assets', 'img')
CONF = os.path.join(SITE, '..', '_ref', 'hero')
PAPEL = '#eee8df'; FPS = 30

def pagina(p, lado):
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    pg = b.new_page(viewport={'width': lado, 'height': lado})
    bin64 = base64.b64encode(open(os.path.join(SITE, 'assets', 'pontos.bin'), 'rb').read()).decode()
    pg.set_content(f'<body style="margin:0;background:{PAPEL}"><canvas id="c" width="{lado}" height="{lado}"></canvas></body>')
    pg.add_script_tag(path=os.path.join(SITE, 'assets', 'js', 'pontos.js'))
    pg.evaluate("""b64 => { const s = atob(b64), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i);
        window.T = pontosGL(document.getElementById('c'), u.buffer, {preserveDrawingBuffer: true}); }""", bin64)
    return b, pg

def quadro(pg, t, formar=False):
    """PNG do canvas já composto sobre o papel (o screenshot pega o fundo do body)."""
    pg.evaluate(f"T.desenhar({t}, 1, {'true' if formar else 'false'})")
    return pg.screenshot(type='png')

def main():
    os.makedirs(VID, exist_ok=True); os.makedirs(CONF, exist_ok=True)
    with sync_playwright() as p:
        if '--teste' in sys.argv:
            b, pg = pagina(p, 720)
            for t in (2, 5, 8.5):
                open(os.path.join(CONF, f'quadro-formar-{t}.png'), 'wb').write(quadro(pg, t, True))
            for t in (0, 6.5, 7.4, 10, 16.5):
                open(os.path.join(CONF, f'quadro-{t}.png'), 'wb').write(quadro(pg, t))
            b.close(); return
        b, pg = pagina(p, 1400)
        ciclo = pg.evaluate('T.ciclo')
        Image.open(io.BytesIO(quadro(pg, 0))).convert('RGB').save(os.path.join(IMG, 'mandala-a.webp'), 'WEBP', quality=88)
        Image.open(io.BytesIO(quadro(pg, 5 + 4.2 + 2))).convert('RGB').save(os.path.join(IMG, 'mandala-b.webp'), 'WEBP', quality=88)
        b.close()
        b, pg = pagina(p, 720)
        mp4 = os.path.join(VID, 'mandala.mp4')
        enc = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'png', '-i', '-',
            '-c:v', 'libx264', '-preset', 'slow', '-crf', '33', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-movflags', '+faststart', '-an', mp4], stdin=subprocess.PIPE)
        q = round(ciclo * FPS)
        for i in range(q):
            enc.stdin.write(quadro(pg, i / FPS))
        enc.stdin.close(); enc.wait(); b.close()
        print(mp4, round(os.path.getsize(mp4) / 1e6, 2), 'MB', q, 'quadros')

if __name__ == '__main__':
    main()
