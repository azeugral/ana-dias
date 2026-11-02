/* Ana Dias: topo, menu, hero de pontos (WebGL no desktop, MP4 no toque), filtros, trilhos e caixa de foto. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var quieto = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- topo e menu ---------- */
  var topo = $('#topo'), menu = $('#menu'), abre = $('#abre-menu');
  function rolou() { topo.classList.toggle('rolou', scrollY > 20); }
  addEventListener('scroll', rolou, { passive: true }); rolou();
  function fecharMenu() { menu.classList.remove('aberto'); topo.classList.remove('menu-aberto'); abre.setAttribute('aria-expanded', 'false'); abre.setAttribute('aria-label', 'Abrir menu'); }
  abre.addEventListener('click', function () {
    var a = !menu.classList.contains('aberto');
    menu.classList.toggle('aberto', a); topo.classList.toggle('menu-aberto', a);
    abre.setAttribute('aria-expanded', a); abre.setAttribute('aria-label', a ? 'Fechar menu' : 'Abrir menu');
  });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', fecharMenu); });
  addEventListener('keydown', function (e) { if (e.key === 'Escape') fecharMenu(); });

  /* ---------- hero ---------- */
  var palco = $('#palco'), canvas = $('#mandala-canvas'), video = $('#mandala-video'), conta = $('#conta');
  var toque = matchMedia('(hover: none), (pointer: coarse)').matches || innerWidth < 1001;
  function fmt(n) { return Math.round(n).toLocaleString('pt-BR'); }

  function usarVideo() {
    document.documentElement.classList.remove('gl');
    if (quieto) return;
    video.src = 'assets/video/mandala.mp4';
    video.addEventListener('playing', function () { palco.classList.add('em-video'); }, { once: true });
    var p = video.play(); if (p && p.catch) p.catch(function () {});
    new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) video.play().catch(function () {}); else video.pause(); }); }).observe(palco);
  }

  function usarWebGL(bin) {
    var T;
    try { T = pontosGL(canvas, bin); } catch (e) { T = null; }
    if (!T) return usarVideo();
    var visivel = true, t0 = null, tPausa = 0, rodando = false, raf;
    function medir() {
      var r = palco.getBoundingClientRect(), d = Math.min(devicePixelRatio || 1, 2);
      var w = Math.round(r.width * d);
      if (canvas.width !== w) { canvas.width = w; canvas.height = w; }
    }
    function quadro(agora) {
      if (t0 === null) t0 = agora - tPausa * 1000;
      var t = (agora - t0) / 1000, s = T.desenhar(t, 1, true);
      conta.textContent = fmt(Math.min(s.rev, 1) * T.n);
      if (visivel) raf = requestAnimationFrame(quadro); else { rodando = false; tPausa = t; t0 = null; }
    }
    function iniciar() { if (!rodando) { rodando = true; raf = requestAnimationFrame(quadro); } }
    medir();
    addEventListener('resize', function () { medir(); if (!rodando) T.desenhar(tPausa, 1, true); });
    canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); cancelAnimationFrame(raf); palco.classList.remove('ao-vivo'); document.documentElement.classList.remove('gl'); conta.textContent = fmt(T.n); });
    new IntersectionObserver(function (es) { visivel = es[0].isIntersecting; if (visivel) iniciar(); }).observe(palco);
    conta.textContent = '0';
    palco.classList.add('ao-vivo');
    iniciar();
  }

  if (quieto) { /* pôster parado */ }
  else if (toque) { addEventListener('load', usarVideo); }
  else {
    fetch('assets/pontos.bin').then(function (r) { if (!r.ok) throw 0; return r.arrayBuffer(); })
      .then(usarWebGL).catch(usarVideo);
  }

  /* ---------- entradas ---------- */
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('viu'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
  $$('.entra').forEach(function (el) { io.observe(el); });

  /* ---------- filtros + ver mais ---------- */
  var obras = $$('.obra'), filtro = 'todos', limite = 12, abertos = false;
  var mais = $('#mais');
  function aplicar() {
    var k = 0;
    obras.forEach(function (o) {
      var ok = filtro === 'todos' || o.dataset.cat === filtro;
      o.classList.toggle('fora', !ok);
      if (ok) k++;
      o.classList.toggle('escondida', ok && !abertos && filtro === 'todos' && k > limite);
    });
    mais.parentNode.hidden = abertos || filtro !== 'todos';
  }
  $$('.filtro').forEach(function (b) {
    b.addEventListener('click', function () {
      filtro = b.dataset.f;
      $$('.filtro').forEach(function (x) { var a = x === b; x.classList.toggle('ativo', a); x.setAttribute('aria-selected', a); });
      aplicar();
    });
  });
  mais.addEventListener('click', function () { abertos = true; aplicar(); });
  aplicar();

  /* ---------- trilhos ---------- */
  $$('.seta-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = document.getElementById(b.dataset.alvo), li = t.querySelector('li');
      t.scrollBy({ left: (li ? li.offsetWidth + 12 : 240) * 2 * +b.dataset.dir, behavior: quieto ? 'auto' : 'smooth' });
    });
  });

  /* ---------- caixa de foto ---------- */
  var caixa = $('#caixa'), cImg = $('#caixa-img'), cLeg = $('#caixa-leg'), atual = 0, lista = [];
  function mostrar(i) {
    atual = (i + lista.length) % lista.length;
    var b = lista[atual], img = b.querySelector('img');
    cImg.src = 'assets/img/obras/' + b.dataset.g + '.webp'; cImg.alt = img.alt; cLeg.textContent = img.alt;
  }
  function abrir(b) {
    lista = obras.filter(function (o) { return !o.classList.contains('fora') && !o.classList.contains('escondida'); }).map(function (o) { return o.querySelector('.obra-btn'); });
    caixa.hidden = false; document.body.style.overflow = 'hidden';
    mostrar(lista.indexOf(b)); $('#caixa-fecha').focus();
  }
  function fechar() { caixa.hidden = true; document.body.style.overflow = ''; if (lista[atual]) lista[atual].focus(); }
  $$('.obra-btn').forEach(function (b) { b.addEventListener('click', function () { abrir(b); }); });
  $('#caixa-fecha').addEventListener('click', fechar);
  $('#caixa-ant').addEventListener('click', function () { mostrar(atual - 1); });
  $('#caixa-prox').addEventListener('click', function () { mostrar(atual + 1); });
  caixa.addEventListener('click', function (e) { if (e.target === caixa) fechar(); });
  addEventListener('keydown', function (e) {
    if (caixa.hidden) return;
    if (e.key === 'Escape') fechar(); else if (e.key === 'ArrowLeft') mostrar(atual - 1); else if (e.key === 'ArrowRight') mostrar(atual + 1);
  });
  var x0 = null;
  caixa.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  caixa.addEventListener('touchend', function (e) {
    if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) mostrar(atual + (dx < 0 ? 1 : -1));
  });
})();
