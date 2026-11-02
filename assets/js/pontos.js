/* Hero: duas mandalas disponíveis da Ana, convertidas em ~26 mil pontos cada (tools/mandalas.py).
   A primeira se forma ponto a ponto, em espiral, como a agulha fechando os anéis; depois os pontos
   viajam de uma mandala para a outra em loop. pontosGL(canvas, dados) devolve {desenhar(t, tam)}:
   t em segundos (o laço é determinístico para o vídeo do celular, tools/gerar_video.py). */
(function () {
  'use strict';
  var FORMAR = 9, SEGURA_A = 5, TROCA = 4.2, SEGURA_B = 5.6;
  var CICLO = SEGURA_A + TROCA + SEGURA_B + TROCA;     // laço sem emenda: A -> B -> A

  var VS = [
    'attribute vec2 aA; attribute vec2 aB; attribute vec2 aInfo;',   // aInfo: tom, ordem
    'uniform float uRev, uMix, uR, uDpr, uT; uniform vec2 uC, uRes;',
    'varying float vTom, vNovo, vViagem;',
    'float h(float n){ return fract(sin(n * 91.345) * 47453.21); }',
    'void main(){',
    '  float ordem = aInfo.y, tom = aInfo.x;',
    '  float ra = length(aA), rb = length(aB);',
    // a troca começa no miolo e corre para fora, cada ponto no seu tempo
    '  float m = clamp((uMix - ra * .42 - h(ordem * 7.0) * .1) / .48, 0.0, 1.0);',
    '  m = m * m * (3.0 - 2.0 * m);',
    '  float ta = atan(aA.y, aA.x), tb = atan(aB.y, aB.x);',
    '  float d = tb - ta; d = d - 6.2831853 * floor((d + 3.1415927) / 6.2831853);',
    '  float giro = sin(m * 3.1415927) * (.55 - ra * .3);',            // redemoinho que volta a zero
    '  float r = mix(ra, rb, m) * (1.0 + sin(m * 3.1415927) * .04);',
    '  float t = ta + d * m + giro;',
    '  vec2 p = vec2(cos(t), sin(t)) * r;',
      '  vec2 px = uC + p * uR;',
    '  gl_Position = vec4(px / uRes * 2.0 - 1.0, 0.0, 1.0); gl_Position.y *= -1.0;',
    '  float vis = step(ordem, uRev);',
    '  float novo = clamp(1.0 - (uRev - ordem) / .018, 0.0, 1.0) * vis;',
    '  vNovo = novo; vTom = tom; vViagem = sin(m * 3.1415927);',
    '  float tam = uR * .0068 * (tom > .5 ? .78 : 1.0) * (1.0 + novo * .9);',
    '  gl_PointSize = max(tam, 1.15) * uDpr;',
  '  if (vis < .5) gl_Position = vec4(9.0, 9.0, 9.0, 1.0);',         // ainda não pontilhado: fora da tela
    '}'].join('\n');

  var FS = [
    'precision mediump float;',
    'varying float vTom, vNovo, vViagem;',
    'uniform vec3 uTinta, uCinza, uVerm;',
    'void main(){',
    '  vec2 q = gl_PointCoord * 2.0 - 1.0; float d = dot(q, q);',
    '  float a = 1.0 - smoothstep(.62, 1.0, d);',
    '  vec3 c = mix(uTinta, uCinza, step(.5, vTom));',
    '  c = mix(c, uVerm, max(vNovo, vViagem * .16));',
    '  a *= vTom > .5 ? .78 : .96;',
    '  gl_FragColor = vec4(c * a, a);',
    '}'].join('\n');

  function cor(hex) { var n = parseInt(hex.slice(1), 16); return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255]; }

  window.pontosGL = function (canvas, bin, opc) {
    opc = opc || {};
    var gl = canvas.getContext('webgl', { antialias: false, premultipliedAlpha: true, alpha: true, preserveDrawingBuffer: !!opc.preserveDrawingBuffer });
    if (!gl) return null;
    function sh(tipo, src) { var s = gl.createShader(tipo); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(s); return s; }
    var pr = gl.createProgram();
    gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr); gl.useProgram(pr);

    var q = new Int16Array(bin), n = q.length / 8;            // 2 mandalas x n x [x, y, tom, ordem]
    var A = new Float32Array(n * 2), B = new Float32Array(n * 2), I = new Float32Array(n * 2), k = 1 / 32767;
    for (var i = 0; i < n; i++) {
      var a = i * 4, b = (n + i) * 4;
      A[i * 2] = q[a] * k; A[i * 2 + 1] = q[a + 1] * k;
      B[i * 2] = q[b] * k; B[i * 2 + 1] = q[b + 1] * k;
      I[i * 2] = q[a + 2]; I[i * 2 + 1] = q[a + 3] * k;
    }
    function buf(dados, nome) {
      var bb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bb); gl.bufferData(gl.ARRAY_BUFFER, dados, gl.STATIC_DRAW);
      var loc = gl.getAttribLocation(pr, nome); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    }
    buf(A, 'aA'); buf(B, 'aB'); buf(I, 'aInfo');
    var U = {};
    ['uRev', 'uMix', 'uR', 'uDpr', 'uT', 'uC', 'uRes', 'uTinta', 'uCinza', 'uVerm'].forEach(function (u) { U[u] = gl.getUniformLocation(pr, u); });
    gl.uniform3fv(U.uTinta, cor(opc.tinta || '#161311'));
    gl.uniform3fv(U.uCinza, cor(opc.cinza || '#6d655d'));
    gl.uniform3fv(U.uVerm, cor(opc.verm || '#c4261d'));
    gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

    /* estado no instante t: quanto já foi pontilhado e quanto da troca A->B */
    function estado(t, comFormacao) {
      if (comFormacao && t < FORMAR) {
        var x = t / FORMAR; return { rev: 1 - Math.pow(1 - x, 1.6), mix: 0 };
      }
      var c = ((comFormacao ? t - FORMAR : t) % CICLO + CICLO) % CICLO, m;
      if (c < SEGURA_A) m = 0;
      else if (c < SEGURA_A + TROCA) m = (c - SEGURA_A) / TROCA;
      else if (c < SEGURA_A + TROCA + SEGURA_B) m = 1;
      else m = 1 - (c - SEGURA_A - TROCA - SEGURA_B) / TROCA;
      return { rev: 2, mix: m };
    }

    return {
      n: n, ciclo: CICLO, formar: FORMAR, estado: estado,
      /* t: segundos; dpr: densidade da tela; comFormacao: se o t=0 começa com o papel vazio */
      desenhar: function (t, dpr, comFormacao) {
        var w = canvas.width, h = canvas.height, s = estado(t, comFormacao);
        gl.viewport(0, 0, w, h); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
        gl.uniform1f(U.uRev, s.rev); gl.uniform1f(U.uMix, s.mix);
        gl.uniform1f(U.uR, Math.min(w, h) * .47); gl.uniform1f(U.uDpr, 1);
        gl.uniform1f(U.uT, t); gl.uniform2f(U.uC, w / 2, h / 2); gl.uniform2f(U.uRes, w, h);
        gl.drawArrays(gl.POINTS, 0, n);
        return s;
      },
      perdido: function () { return gl.isContextLost(); }
    };
  };
})();
