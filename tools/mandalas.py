"""Transforma as 4 mandalas do flash da Ana (post CqTwCJ_LGfy, foto 3: o iPad com as artes disponíveis)
em pontos para o hero (assets/js/pontos.js).

Passos por mandala: recorte -> elipse da perspectiva vira círculo -> classes de tinta (preto, cinza, vermelho)
-> simetria rotacional (média das N rotações, limpa o reflexo da tela) -> mapa de densidade -> pontilhismo
por Lloyd ponderado (Secord 2002) -> ordem de aparição em espiral, como a agulha fechando os anéis.

Saída: assets/pontos.bin (Int16: para cada mandala, N x [x, y, tom, ordem]; x, y, ordem em /32767) + _ref/hero/*.png de conferência.
Uso: python tools/mandalas.py"""
import os, json
import numpy as np, cv2
from scipy.spatial import cKDTree

AQUI = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(AQUI)
REF = os.path.join(SITE, '..', '_ref'); CONF = os.path.join(REF, 'hero'); os.makedirs(CONF, exist_ok=True)
IPAD = os.path.join(REF, 'ig', '133_CqTwCJ_LGfy_3.jpg')       # flash no iPad (em perspectiva)
DISP = os.path.join(REF, 'hl', 'disponiveis_{}.jpg')           # destaque Disponíveis (arte reta)
N = 26000          # pontos por mandala (todas iguais, para a troca entre elas)
S = 900            # lado do mapa de densidade
# (arquivo, recorte x0, y0, x1, y1); a simetria é achada sozinha
# as do iPad (perspectiva + reflexo) borravam na simetria; ficam as duas retas do destaque
RECORTES = [(DISP.format('02'), (0, 20, 420, 450)), (DISP.format('03'), (10, 20, 400, 410))]

def retificar(img):
    """Acha a elipse da mandala (perspectiva do iPad) e devolve um quadrado SxS com ela redonda e centrada."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    L, a = lab[..., 0].astype(float), lab[..., 1].astype(float)
    papel = np.percentile(L, 90)
    tinta = ((L < papel - 30) | (a > 150)).astype(np.uint8) * 255
    tinta = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
    h0, w0 = L.shape
    # só o miolo do recorte: as quinas têm a moldura do iPad
    yy, xx = np.mgrid[:h0, :w0]
    tinta[np.hypot(xx - w0 / 2, yy - h0 / 2) > min(w0, h0) * .5] = 0
    tinta = cv2.morphologyEx(tinta, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(tinta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = np.vstack(sorted(cs, key=cv2.contourArea)[-40:])   # pétalas soltas da borda entram no casco
    hull = cv2.convexHull(c)
    (cx, cy), (w, h), ang = cv2.fitEllipse(hull)
    # afim que leva a elipse ao círculo de raio .47 S no centro
    t = np.deg2rad(ang)
    R = np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])   # gira para os eixos da elipse
    Sc = np.diag([S * .94 / w, S * .94 / h])
    M = R.T @ Sc @ R
    off = np.array([S / 2, S / 2]) - M @ np.array([cx, cy])
    A = np.hstack([M, off[:, None]])
    return cv2.warpAffine(img, A, (S, S), flags=cv2.INTER_CUBIC, borderValue=(215, 210, 212))

def classes(img):
    """Mapa de tinta 0..1 (preto 1, cinza ~.42) e máscara do vermelho."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(float)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(float)
    L = lab[..., 0] / 255
    verm = ((hsv[..., 1] > 110) & ((hsv[..., 0] < 10) | (hsv[..., 0] > 165)) & (hsv[..., 2] > 90)).astype(float)
    papel = np.percentile(L, 90)
    escuro = np.clip((papel - L) / (papel - .1), 0, 1)
    escuro = np.where(verm > 0, 0, escuro)
    # preto chapado vira 1, cinza do flash vira meio-tom
    dens = np.where(escuro > .62, 1.0, np.where(escuro > .2, .42, 0))
    return dens, verm

def simetrizar(m, n):
    acc = np.zeros_like(m)
    for k in range(n):
        R = cv2.getRotationMatrix2D((S / 2, S / 2), 360 * k / n, 1)
        acc += cv2.warpAffine(m, R, (S, S), flags=cv2.INTER_LINEAR)
    return acc / n

def achar_simetria(m):
    """Número de pétalas: a rotação de 360/n que mais se parece com a original (o maior n entre os empatados)."""
    sc = {}
    for n in range(4, 25):
        R = cv2.getRotationMatrix2D((S / 2, S / 2), 360 / n, 1)
        r = cv2.warpAffine(m, R, (S, S))
        sc[n] = np.corrcoef(m.ravel(), r.ravel())[0, 1]
    top = max(sc.values())
    return max(n for n, v in sc.items() if v > top - .03), sc

def pontilhar(dens, n, iters=36, seed=7):
    rng = np.random.default_rng(seed)
    ys, xs = np.nonzero(dens > .02)
    w = dens[ys, xs]
    p = w / w.sum()
    idx = rng.choice(len(xs), n, p=p)
    pts = np.stack([xs[idx], ys[idx]], 1).astype(float) + rng.random((n, 2)) - .5
    pix = np.stack([xs, ys], 1).astype(float)
    for _ in range(iters):
        _, lab = cKDTree(pts).query(pix, workers=-1)
        sw = np.bincount(lab, w, n)
        sx = np.bincount(lab, w * pix[:, 0], n); sy = np.bincount(lab, w * pix[:, 1], n)
        ok = sw > 0
        pts[ok, 0] = sx[ok] / sw[ok]; pts[ok, 1] = sy[ok] / sw[ok]
    return pts

def main():
    todas = []
    for i, (arq, (x0, y0, x1, y1)) in enumerate(RECORTES):
        q = retificar(cv2.imread(arq)[y0:y1, x0:x1])
        dens, verm = classes(q)
        n, _ = achar_simetria(cv2.GaussianBlur(dens, (0, 0), 3))
        print('mandala', i + 1, 'simetria', n)
        dens = simetrizar(dens, n); verm = simetrizar(verm, n)
        # bordas dos desenhos do flash: o ponto da Ana deixa um respiro claro entre as formas
        tot = np.clip(dens + verm * .9, 0, 1)
        r = np.hypot(*np.meshgrid(np.arange(S) - S / 2, np.arange(S) - S / 2))
        tot[r > S * .485] = 0
        tot = cv2.GaussianBlur(tot, (0, 0), 1.2) ** 1.15
        pts = pontilhar(tot, N, seed=11 + i)
        xi = np.clip(pts[:, 0].round().astype(int), 0, S - 1); yi = np.clip(pts[:, 1].round().astype(int), 0, S - 1)
        tom = np.where(verm[yi, xi] > .45, 2, np.where(dens[yi, xi] < .7, 1, 0)).astype(float)
        # ordem: espiral de dentro para fora, anel por anel, com um pouco de acaso
        dx = (pts[:, 0] - S / 2) / (S / 2); dy = (pts[:, 1] - S / 2) / (S / 2)
        rr = np.hypot(dx, dy); th = (np.arctan2(dy, dx) / (2 * np.pi)) % 1
        chave = np.floor(rr * 14) + th + np.random.default_rng(i).random(N) * .35
        ordem = np.argsort(np.argsort(chave)) / (N - 1)
        # ordena pelos raios para que a troca de mandala leve cada ponto ao "mesmo anel" na outra
        o = np.lexsort((th, rr))
        arr = np.stack([dx, dy, tom, ordem], 1)[o].astype(np.float32)
        todas.append(arr)
        cv2.imwrite(os.path.join(CONF, f'retificada-{i + 1}.png'), q)
        cv2.imwrite(os.path.join(CONF, f'densidade-{i + 1}.png'), (255 - tot * 255).astype(np.uint8))
        prev = np.full((S, S, 3), 14, np.uint8)
        cor = {0: (220, 228, 236), 1: (120, 124, 130), 2: (40, 50, 215)}
        for (x, y), t in zip(pts, tom):
            cv2.circle(prev, (int(x), int(y)), 1, cor[int(t)], -1, cv2.LINE_AA)
        cv2.imwrite(os.path.join(CONF, f'pontos-{i + 1}.png'), prev)
        print('mandala', i + 1, 'tons', np.bincount(tom.astype(int), minlength=3))
    out = os.path.join(SITE, 'assets', 'pontos.bin')
    tudo = np.concatenate(todas)
    q = np.round(tudo * np.array([32767, 32767, 1, 32767])).astype('<i2')   # Int16: x, y, tom, ordem
    q.tofile(out)
    json.dump({'n': N, 'mandalas': len(todas)}, open(os.path.join(CONF, 'pontos.json'), 'w'))
    print(out, round(os.path.getsize(out) / 1e6, 2), 'MB')

if __name__ == '__main__':
    main()
