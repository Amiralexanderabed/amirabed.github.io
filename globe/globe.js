/* Biosphere — an interactive globe of Earth's terrestrial ecoregions.
 * Dependency-free WebGL2. Data: RESOLVE Ecoregions 2017, WorldClim 2.1, NASA Blue Marble.
 */
(() => {
'use strict';

/* Bump DATA_VERSION whenever anything in data/ is rebuilt: these files are
   served with far-future caching, so without it browsers keep the old copy. */
const DATA_VERSION = '4';
const DATA = 'data/';
const url = f => `${DATA}${f}?v=${DATA_VERSION}`;
const $ = id => document.getElementById(id);

/* ------------------------------------------------------------------ math */
const M4 = {
  perspective(fovy, aspect, near, far) {
    const f = 1 / Math.tan(fovy / 2), nf = 1 / (near - far);
    return new Float32Array([
      f / aspect,0,0,0,  0,f,0,0,  0,0,(far + near) * nf,-1,  0,0,2 * far * near * nf,0]);
  },
  lookAt(eye, center, up) {
    let z0 = eye[0] - center[0], z1 = eye[1] - center[1], z2 = eye[2] - center[2];
    let l = 1 / Math.hypot(z0, z1, z2); z0 *= l; z1 *= l; z2 *= l;
    let x0 = up[1] * z2 - up[2] * z1, x1 = up[2] * z0 - up[0] * z2, x2 = up[0] * z1 - up[1] * z0;
    l = Math.hypot(x0, x1, x2); l = l ? 1 / l : 0; x0 *= l; x1 *= l; x2 *= l;
    const y0 = z1 * x2 - z2 * x1, y1 = z2 * x0 - z0 * x2, y2 = z0 * x1 - z1 * x0;
    return new Float32Array([
      x0,y0,z0,0, x1,y1,z1,0, x2,y2,z2,0,
      -(x0 * eye[0] + x1 * eye[1] + x2 * eye[2]),
      -(y0 * eye[0] + y1 * eye[1] + y2 * eye[2]),
      -(z0 * eye[0] + z1 * eye[1] + z2 * eye[2]), 1]);
  },
  mul(a, b) {
    const o = new Float32Array(16);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
      let s = 0;
      for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k];
      o[c * 4 + r] = s;
    }
    return o;
  }
};

const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const DEG = Math.PI / 180;

/** Unit-sphere position for a lat/lon in radians. */
function llToVec(lat, lon) {
  const c = Math.cos(lat);
  return [c * Math.sin(lon), Math.sin(lat), c * Math.cos(lon)];
}
/** Inverse of llToVec. */
function vecToLL(p) {
  return [Math.asin(clamp(p[1], -1, 1)), Math.atan2(p[0], p[2])];
}

/* --------------------------------------------------------------- shaders */
const VS_GLOBE = `#version 300 es
layout(location=0) in vec3 aPos;
layout(location=1) in vec2 aUV;
uniform mat4 uVP;
uniform float uScale;
out vec3 vPos;
out vec2 vUV;
void main(){
  vPos = aPos * uScale;
  vUV = aUV;
  gl_Position = uVP * vec4(vPos, 1.0);
}`;

const FS_GLOBE = `#version 300 es
precision highp float;
precision highp int;

in vec3 vPos;
in vec2 vUV;
out vec4 fragColor;

uniform sampler2D uBase;
uniform sampler2D uEco;
uniform sampler2D uMarine;
uniform sampler2D uClim;
uniform sampler2D uRelief;
uniform sampler2D uLut;

uniform vec3  uCam;
uniform vec3  uLight;
uniform int   uMode;
uniform float uOpacity;
uniform float uReliefAmt;
uniform int   uHiIdx;
uniform int   uHiSea;
uniform vec2  uEcoSize;
uniform vec2  uClimSize;
uniform vec2  uReliefSize;

vec2 dataSize(){ return uMode == 3 ? uClimSize : uEcoSize; }

int ecoAt(vec2 uv){
  ivec2 c = ivec2(clamp(uv * uEcoSize, vec2(0.0), uEcoSize - 1.0));
  vec4 t = texelFetch(uEco, c, 0);
  return int(t.r * 255.0 + 0.5) + int(t.g * 255.0 + 0.5) * 256;
}

int seaAt(vec2 uv){
  ivec2 c = ivec2(clamp(uv * uEcoSize, vec2(0.0), uEcoSize - 1.0));
  vec4 t = texelFetch(uMarine, c, 0);
  return int(t.r * 255.0 + 0.5) + int(t.g * 255.0 + 0.5) * 256;
}

vec4 dataAt(vec2 uv){
  int idx = ecoAt(uv);
  if(uMode == 3){
    /* Koppen is derived from land climate data only; the sea stays bare. */
    if(idx == 0) return vec4(0.0);
    ivec2 c = ivec2(clamp(uv * uClimSize, vec2(0.0), uClimSize - 1.0));
    int k = int(texelFetch(uClim, c, 0).r * 255.0 + 0.5);
    if(k == 0) return vec4(0.0);
    return texelFetch(uLut, ivec2(k, 4), 0);
  }
  if(idx > 0){
    int row = uMode == 1 ? 0 : (uMode == 2 ? 2 : (uMode == 4 ? 1 : 3));
    return texelFetch(uLut, ivec2(idx, row), 0);
  }
  /* sea: rows 5 biome, 6 realm, 7 individual region. No marine equivalent of
     the terrestrial protection assessment, so mode 5 leaves it clear. */
  if(uMode == 5) return vec4(0.0);
  int m = seaAt(uv);
  if(m == 0) return vec4(0.0);
  return texelFetch(uLut, ivec2(m, uMode == 2 ? 7 : (uMode == 4 ? 6 : 5)), 0);
}

/* 4-tap rotated-grid average over the pixel footprint: stops the index
   texture from shimmering when the globe is small on screen. */
vec4 dataAA(vec2 uv){
  vec2 fw = min(fwidth(uv), vec2(0.02));
  vec2 sz = dataSize();
  if(fw.x * sz.x < 0.9 && fw.y * sz.y < 0.9){
    /* Magnified. Blend the four neighbouring categories with a steep ramp so
       region interiors stay flat and only the boundary softens - otherwise the
       nearest-neighbour edges read as staircases. */
    vec2 p = uv * sz - 0.5;
    vec2 f = smoothstep(0.30, 0.70, fract(p));
    vec2 b = (floor(p) + 0.5) / sz, st = 1.0 / sz;
    return mix(mix(dataAt(b),                    dataAt(b + vec2(st.x, 0.0)), f.x),
               mix(dataAt(b + vec2(0.0, st.y)),  dataAt(b + st),              f.x), f.y);
  }
  vec4 a = dataAt(uv + vec2(-0.375, -0.125) * fw)
         + dataAt(uv + vec2( 0.125, -0.375) * fw)
         + dataAt(uv + vec2( 0.375,  0.125) * fw)
         + dataAt(uv + vec2(-0.125,  0.375) * fw);
  return a * 0.25;
}

float hAt(vec2 uv){ return texture(uRelief, uv).r; }

float hillshade(vec2 uv, float lat){
  vec2 px = 1.0 / uReliefSize;
  float cl = max(cos(lat), 0.20);
  float sx = (hAt(uv + vec2(px.x, 0.0)) - hAt(uv - vec2(px.x, 0.0))) / cl;
  float sy =  hAt(uv + vec2(0.0, px.y)) - hAt(uv - vec2(0.0, px.y));
  vec3 n = normalize(vec3(-sx * 3.0, -sy * 3.0, 1.0));
  return clamp(dot(n, normalize(vec3(-0.6, -0.6, 0.75))), 0.0, 1.0);
}

void main(){
  vec3 N = normalize(vPos);
  vec3 V = normalize(uCam - vPos);
  int idx = ecoAt(vUV);

  vec3 base = texture(uBase, vUV).rgb;
  vec3 col = base;

  if(uMode != 0 && uOpacity > 0.001){
    vec4 d = dataAA(vUV);
    float luma = dot(base, vec3(0.299, 0.587, 0.114));
    /* Land imagery carries real texture worth keeping; open water is uniformly
       dark, so lift its floor or every sea colour comes out muddy. */
    float lm = idx > 0 ? luma : max(luma, 0.46);
    vec3 tint = d.rgb * (0.70 + 0.60 * lm);
    col = mix(col, tint, clamp(d.a, 0.0, 1.0) * uOpacity);
  }

  if(uReliefAmt > 0.001 && idx > 0){
    float lat = (0.5 - vUV.y) * 3.14159265;
    col *= mix(1.0, 0.55 + 0.75 * hillshade(vUV, lat), uReliefAmt);
  }

  if(uHiIdx > 0 && idx == uHiIdx) col = mix(col, vec3(0.85, 1.0, 0.95), 0.20);
  if(uHiSea > 0 && idx == 0 && seaAt(vUV) == uHiSea) col = mix(col, vec3(0.85, 1.0, 0.95), 0.20);

  float ndl = dot(N, uLight);
  col *= 0.60 + 0.40 * smoothstep(-0.40, 0.55, ndl);

  float fres = pow(1.0 - max(dot(N, V), 0.0), 3.5);
  col += vec3(0.20, 0.42, 0.78) * fres * 0.60 * (0.30 + 0.70 * smoothstep(-0.25, 0.5, ndl));

  fragColor = vec4(col, 1.0);
}`;

const FS_ATMO = `#version 300 es
precision highp float;
in vec3 vPos;
in vec2 vUV;
out vec4 fragColor;
uniform vec3 uCam;
uniform vec3 uLight;
void main(){
  vec3 N = normalize(vPos);
  vec3 V = normalize(uCam - vPos);
  float rim = pow(1.0 - max(dot(N, V), 0.0), 2.6);
  float lit = smoothstep(-0.55, 0.45, dot(N, uLight));
  fragColor = vec4(vec3(0.26, 0.52, 0.95) * rim * 0.95 * (0.10 + 0.90 * lit), 1.0);
}`;

const VS_BG = `#version 300 es
layout(location=0) in vec2 aPos;
out vec2 vNdc;
void main(){ vNdc = aPos; gl_Position = vec4(aPos, 0.999999, 1.0); }`;

const FS_BG = `#version 300 es
precision highp float;
in vec2 vNdc;
out vec4 fragColor;
uniform vec3 uRight, uUp, uFwd;
uniform float uTanHalf, uAspect;

float hash31(vec3 p){
  p = fract(p * vec3(443.897, 441.423, 437.195));
  p += dot(p, p.yzx + 19.19);
  return fract((p.x + p.y) * p.z);
}
float layer(vec3 d, float density, float size){
  vec3 p = d * density;
  vec3 c = floor(p), f = fract(p);
  float h = hash31(c);
  if(h < 0.955) return 0.0;
  vec3 sp = vec3(hash31(c + 1.31), hash31(c + 2.73), hash31(c + 4.17));
  float br = 0.30 + 0.70 * fract(h * 97.13);
  return smoothstep(size, 0.0, length(f - sp)) * br;
}
void main(){
  vec3 d = normalize(uFwd + uRight * (vNdc.x * uTanHalf * uAspect) + uUp * (vNdc.y * uTanHalf));
  float s = layer(d, 46.0, 0.34) * 0.85 + layer(d, 96.0, 0.30) * 0.55 + layer(d, 170.0, 0.26) * 0.35;
  vec3 col = vec3(0.016, 0.021, 0.036) + vec3(0.004, 0.006, 0.014) * (1.0 - abs(vNdc.y));
  col += vec3(0.92, 0.95, 1.0) * s;
  fragColor = vec4(col, 1.0);
}`;

/* ------------------------------------------------------------------ gl */
const canvas = $('gl');
const gl = canvas.getContext('webgl2', {
  antialias: true, alpha: false, depth: true,
  powerPreference: 'high-performance', preserveDrawingBuffer: false
});
if (!gl) { $('loader').style.display = 'none'; $('nogl').style.display = 'flex'; return; }

function compile(type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src); gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
  return s;
}
function program(vs, fs) {
  const p = gl.createProgram();
  gl.attachShader(p, compile(gl.VERTEX_SHADER, vs));
  gl.attachShader(p, compile(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
  const u = {};
  const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
  for (let i = 0; i < n; i++) {
    const name = gl.getActiveUniform(p, i).name.replace(/\[0\]$/, '');
    u[name] = gl.getUniformLocation(p, name);
  }
  return { p, u };
}

/* --------------------------------------------------------- sphere mesh */
function buildSphere(latSegs, lonSegs) {
  const nv = (latSegs + 1) * (lonSegs + 1);
  const pos = new Float32Array(nv * 3), uv = new Float32Array(nv * 2);
  let k = 0;
  for (let i = 0; i <= latSegs; i++) {
    const v = i / latSegs, lat = (0.5 - v) * Math.PI;
    const cl = Math.cos(lat), sl = Math.sin(lat);
    for (let j = 0; j <= lonSegs; j++, k++) {
      const u = j / lonSegs, lon = (u - 0.5) * 2 * Math.PI;
      pos[k * 3] = cl * Math.sin(lon); pos[k * 3 + 1] = sl; pos[k * 3 + 2] = cl * Math.cos(lon);
      uv[k * 2] = u; uv[k * 2 + 1] = v;
    }
  }
  const idx = new Uint32Array(latSegs * lonSegs * 6);
  let m = 0;
  for (let i = 0; i < latSegs; i++) for (let j = 0; j < lonSegs; j++) {
    const a = i * (lonSegs + 1) + j, b = a + lonSegs + 1;
    idx[m++] = a; idx[m++] = b; idx[m++] = a + 1;
    idx[m++] = a + 1; idx[m++] = b; idx[m++] = b + 1;
  }
  return { pos, uv, idx, count: idx.length };
}

/* ----------------------------------------------------------- resources */
function loadImage(url) {
  return new Promise((res, rej) => {
    const im = new Image();
    im.onload = () => res(im);
    im.onerror = () => rej(new Error('failed to load ' + url));
    im.src = url;
  });
}
/** Decode a PNG once, keeping the pixels for CPU lookups and the GPU alike. */
async function decodePng(url) {
  const im = await loadImage(url);
  const c = document.createElement('canvas');
  c.width = im.width; c.height = im.height;
  const ctx = c.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(im, 0, 0);
  const d = ctx.getImageData(0, 0, im.width, im.height);
  return { w: im.width, h: im.height, px: d.data };
}
function texFromPixels(px, w, h, filter) {
  const t = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, t);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, px);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filter);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filter);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  return t;
}
/** Index raster as RG8 for the GPU plus a Uint16Array for picking.
 *  The decoded RGBA bitmap (33 MB per raster) is dropped straight afterwards. */
function indexRaster(d) {
  const n = d.w * d.h, rg = new Uint8Array(n * 2), idx = new Uint16Array(n);
  for (let i = 0; i < n; i++) {
    const r = d.px[i * 4], g = d.px[i * 4 + 1];
    rg[i * 2] = r; rg[i * 2 + 1] = g;
    idx[i] = r + g * 256;
  }
  return { w: d.w, h: d.h, idx, tex: texRG8(rg, d.w, d.h) };
}

function texRG8(rg, w, h) {
  const t = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, t);
  gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RG8, w, h, 0, gl.RG, gl.UNSIGNED_BYTE, rg);
  gl.pixelStorei(gl.UNPACK_ALIGNMENT, 4);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  return t;
}

function texFromImage(img) {
  const t = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, t);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, gl.RGBA, gl.UNSIGNED_BYTE, img);
  gl.generateMipmap(gl.TEXTURE_2D);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  const aniso = gl.getExtension('EXT_texture_filter_anisotropic');
  if (aniso) {
    const max = gl.getParameter(aniso.MAX_TEXTURE_MAX_ANISOTROPY_EXT);
    gl.texParameterf(gl.TEXTURE_2D, aniso.TEXTURE_MAX_ANISOTROPY_EXT, Math.min(8, max));
  }
  return t;
}
/** Relief is stored as hi/lo bytes; recombine into a filterable float texture. */
function texRelief(d) {
  const n = d.w * d.h, f = new Float32Array(n);
  for (let i = 0; i < n; i++) f[i] = (d.px[i * 4] + d.px[i * 4 + 1] / 255) / 255;
  const t = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, t);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.R16F, d.w, d.h, 0, gl.RED, gl.FLOAT, f);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  return t;
}

const REALM_COLOR = { AF:'#e0913a', AN:'#cfe3ee', AU:'#d9605c', IN:'#9b6fd0',
                      NE:'#4a90d9', NO:'#3fb27f', OC:'#46c8d0', PA:'#e0c04a' };
const NNH_COLOR = { 1:'#2f9e5e', 2:'#8fc93a', 3:'#f0a03a', 4:'#e05252' };

function hexRgb(h) {
  const v = parseInt(h.replace('#', '').slice(0, 6), 16);
  return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
}

/** Distinct colour per marine unit: hue from its province so provinces read as
 *  blocks, lightness jittered per region so neighbours stay separable. */
function hslHex(h, s, l) {
  const f = n => {
    const k = (n + h * 12) % 12, a = s * Math.min(l, 1 - l);
    const v = l - a * Math.max(-1, Math.min(k - 3, Math.min(9 - k, 1)));
    return Math.round(v * 255).toString(16).padStart(2, '0');
  };
  return '#' + f(0) + f(8) + f(4);
}

/** 1024x8 lookup texture: one row per colouring scheme. */
function buildLut(meta, marine, biota) {
  const W = 1024, H = 8, px = new Uint8Array(W * H * 4);
  const put = (x, y, hex, a) => {
    if (x < 0 || x >= W) return;
    const c = hexRgb(hex), o = (y * W + x) * 4;
    px[o] = c[0]; px[o + 1] = c[1]; px[o + 2] = c[2]; px[o + 3] = a === undefined ? 255 : a;
  };
  meta.ecoregions.forEach((e, i) => {
    const x = i + 1;
    const b = biota.biomes[String(e.biome)];
    put(x, 0, b ? b.color : '#5a6070');
    put(x, 1, REALM_COLOR[e.code ? e.code.slice(0, 2) : ''] || '#5a6070');
    put(x, 2, e.color || '#5a6070');
    put(x, 3, NNH_COLOR[e.nnh] || '#5a6070');
  });
  meta.koppenColors.forEach((hex, i) => { if (i > 0) put(i, 4, hex); });

  const provIdx = {};
  marine.units.forEach(u => { if (!(u.province in provIdx)) provIdx[u.province] = Object.keys(provIdx).length; });
  marine.units.forEach((u, i) => {
    const x = i + 1;
    const mb = biota.marine.biomes[u.biome];
    put(x, 5, mb ? mb.color : '#3a63c0');
    put(x, 6, biota.marine.realmColors[u.realm] || '#3a63c0');
    // Golden-ratio hue walk keeps neighbouring provinces apart, confined to
    // green-through-violet so the sea still reads as sea.
    const h = 0.42 + ((provIdx[u.province] * 0.6180339887) % 1) * 0.45;
    put(x, 7, hslHex(h, 0.52, 0.36 + ((i * 37) % 5) * 0.055));
  });
  return texFromPixels(px, W, H, gl.NEAREST);
}

/* ------------------------------------------------------------------ app */
const FOV = 46 * DEG;
/* Zoom floor. The imagery and the ecoregion raster are single global textures
   at roughly 6.5 km and 9.8 km per texel, so past this point you are just
   magnifying texels - no reachable distance stays sharp without tiled imagery.
   1.15 shows about 2,500 km across, which is the scale ecoregions live at. */
const MIN_D = 1.15, MAX_D = 7.5;
const state = {
  lat: 14 * DEG, lon: 16 * DEG, dist: 6.2,       // rendered (damped)
  tLat: 14 * DEG, tLon: 16 * DEG, tDist: 2.9,    // target
  vLat: 0, vLon: 0,                              // inertia
  mode: 1, opacity: 0.8, relief: 1, spin: false,
  hover: 0, sel: 0, hoverSea: 0, selSea: 0, dirty: true, showFps: false
};
let R = {};   // resources, filled during boot

const aspect = () => canvas.width / canvas.height;
/** Half-height of the view plane at unit depth. On portrait viewports the
 *  horizontal FOV is held constant instead, so the globe never overflows. */
const tanHalf = () => {
  const a = aspect(), f = Math.tan(FOV / 2);
  return a >= 1 ? f : f / a;
};

function camBasis() {
  const lat = clamp(state.lat, -89.3 * DEG, 89.3 * DEG);
  const e = llToVec(lat, state.lon);
  const eye = [e[0] * state.dist, e[1] * state.dist, e[2] * state.dist];
  const fwd = [-e[0], -e[1], -e[2]];
  // right = fwd x worldUp, up = right x fwd  (matches M4.lookAt with up = +Y)
  let rx = -fwd[2], rz = fwd[0];
  const rl = Math.hypot(rx, rz) || 1; rx /= rl; rz /= rl;
  const up = [-rz * fwd[1], rz * fwd[0] - rx * fwd[2], rx * fwd[1]];
  return { eye, fwd, right: [rx, 0, rz], up };
}

/** Screen point -> {lat, lon} on the globe, or null if the ray misses. */
function rayPick(clientX, clientY) {
  const r = canvas.getBoundingClientRect();
  const nx = ((clientX - r.left) / r.width) * 2 - 1;
  const ny = 1 - ((clientY - r.top) / r.height) * 2;
  const b = camBasis(), th = tanHalf(), a = aspect();
  let d = [
    b.fwd[0] + b.right[0] * nx * th * a + b.up[0] * ny * th,
    b.fwd[1] + b.right[1] * nx * th * a + b.up[1] * ny * th,
    b.fwd[2] + b.right[2] * nx * th * a + b.up[2] * ny * th];
  const dl = Math.hypot(d[0], d[1], d[2]); d = [d[0] / dl, d[1] / dl, d[2] / dl];
  const e = b.eye;
  const bb = e[0] * d[0] + e[1] * d[1] + e[2] * d[2];
  const cc = e[0] * e[0] + e[1] * e[1] + e[2] * e[2] - 1;
  const disc = bb * bb - cc;
  if (disc < 0) return null;
  const t = -bb - Math.sqrt(disc);
  if (t < 0) return null;
  const p = [e[0] + d[0] * t, e[1] + d[1] * t, e[2] + d[2] * t];
  const ll = vecToLL(p);
  return { lat: ll[0], lon: ll[1] };
}

/* ------------------------------------------------------- data lookups */
const PMAX = Math.log(12001);
function sampleUV(lat, lon) {
  let u = lon / (2 * Math.PI) + 0.5;
  u = u - Math.floor(u);
  const v = clamp(0.5 - lat / Math.PI, 0, 0.999999);
  return [u, v];
}
function rasterAt(d, lat, lon) {
  const [u, v] = sampleUV(lat, lon);
  const x = Math.min(d.w - 1, (u * d.w) | 0), y = Math.min(d.h - 1, (v * d.h) | 0);
  return d.idx[y * d.w + x];
}
const ecoAt = (lat, lon) => rasterAt(R.eco, lat, lon);
const seaAt = (lat, lon) => rasterAt(R.marine, lat, lon);
/** Nearest pixel holding a real ecoregion — place markers can land on ice or water. */
function ecoNear(lat, lon, maxRing) {
  const hit = ecoAt(lat, lon);
  if (hit && R.meta.ecoregions[hit - 1].biome > 0) return hit;
  const d = R.eco, [u, v] = sampleUV(lat, lon);
  const cx = Math.min(d.w - 1, (u * d.w) | 0), cy = Math.min(d.h - 1, (v * d.h) | 0);
  for (let r = 2; r <= (maxRing || 48); r += 2) {
    for (let a = 0; a < 32; a++) {
      const t = a / 32 * 2 * Math.PI;
      const x = ((cx + Math.round(Math.cos(t) * r)) % d.w + d.w) % d.w;
      const y = clamp(cy + Math.round(Math.sin(t) * r), 0, d.h - 1);
      const idx = d.idx[y * d.w + x];
      if (idx && R.meta.ecoregions[idx - 1].biome > 0) return idx;
    }
  }
  return hit;
}

function climateAt(lat, lon) {
  const [u, v] = sampleUV(lat, lon), a = R.climA, b = R.climB;
  const x = Math.min(a.w - 1, (u * a.w) | 0), y = Math.min(a.h - 1, (v * a.h) | 0);
  const o = (y * a.w + x) * 4;
  const k = a.px[o];
  if (!k) return null;
  return {
    koppen: k,
    temp: a.px[o + 1] / 2 - 60,
    precip: Math.expm1(a.px[o + 2] / 255 * PMAX),
    tCold: b.px[o] / 2 - 60,
    tHot: b.px[o + 1] / 2 - 60,
    pDry: Math.expm1(b.px[o + 2] / 255 * PMAX)
  };
}

/* --------------------------------------------------------- interaction */
let drag = null, moved = 0, lastPointer = null;

function pixelToAngle() {
  // world units travelled by the surface under one pixel at screen centre
  return 2 * (state.dist - 1) * tanHalf() / canvas.clientHeight;
}

function applyDrag(dx, dy) {
  const k = pixelToAngle();
  const cl = Math.max(Math.cos(state.tLat), 0.25);
  const dLon = -dx * k / cl, dLat = dy * k;
  state.tLon += dLon;
  state.tLat = clamp(state.tLat + dLat, -89.3 * DEG, 89.3 * DEG);
  state.vLon = dLon; state.vLat = dLat;
  state.dirty = true;
}

function zoomBy(factor, clientX, clientY) {
  const old = state.tDist;
  state.tDist = clamp(state.tDist * factor, MIN_D, MAX_D);
  if (clientX !== undefined && state.tDist < old) {
    const p = rayPick(clientX, clientY);
    if (p) {
      const f = (1 - state.tDist / old) * 0.85;
      let dl = p.lon - state.tLon;
      while (dl > Math.PI) dl -= 2 * Math.PI;
      while (dl < -Math.PI) dl += 2 * Math.PI;
      state.tLon += dl * f;
      state.tLat = clamp(state.tLat + (p.lat - state.tLat) * f, -89.3 * DEG, 89.3 * DEG);
    }
  }
  state.dirty = true;
}

canvas.addEventListener('pointerdown', e => {
  if (e.button !== 0 && e.pointerType === 'mouse') return;
  canvas.setPointerCapture(e.pointerId);
  drag = { x: e.clientX, y: e.clientY, id: e.pointerId };
  moved = 0;
  state.vLat = state.vLon = 0;
  canvas.classList.add('dragging');
  hideHint();
});
canvas.addEventListener('pointermove', e => {
  lastPointer = { x: e.clientX, y: e.clientY };
  if (drag && e.pointerId === drag.id) {
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    moved += Math.abs(dx) + Math.abs(dy);
    applyDrag(dx, dy);
    drag.x = e.clientX; drag.y = e.clientY;
    hideTip();
  } else {
    queueHover();
  }
});
function endDrag(e) {
  if (!drag || e.pointerId !== drag.id) return;
  drag = null;
  canvas.classList.remove('dragging');
  state.dirty = true;
}
canvas.addEventListener('pointerup', e => {
  const wasDrag = drag && moved > 6;
  endDrag(e);
  if (!wasDrag) selectAt(e.clientX, e.clientY);
});
canvas.addEventListener('pointercancel', endDrag);
canvas.addEventListener('pointerleave', () => {
  hideTip(); state.hover = state.hoverSea = 0; state.dirty = true;
});

canvas.addEventListener('wheel', e => {
  e.preventDefault();
  const d = Math.max(-120, Math.min(120, e.deltaY * (e.deltaMode === 1 ? 16 : 1)));
  zoomBy(Math.exp(d * 0.0016), e.clientX, e.clientY);
  hideHint();
}, { passive: false });

/* pinch */
const touches = new Map();
let pinch = null;
canvas.addEventListener('pointerdown', e => { if (e.pointerType === 'touch') touches.set(e.pointerId, e); });
canvas.addEventListener('pointermove', e => {
  if (e.pointerType !== 'touch') return;
  if (!touches.has(e.pointerId)) return;
  touches.set(e.pointerId, e);
  if (touches.size === 2) {
    const [a, b] = [...touches.values()];
    const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
    if (pinch) {
      zoomBy(clamp(pinch / d, 0.5, 2));
      drag = null; canvas.classList.remove('dragging');
    }
    pinch = d;
  }
});
const dropTouch = e => { touches.delete(e.pointerId); if (touches.size < 2) pinch = null; };
canvas.addEventListener('pointerup', dropTouch);
canvas.addEventListener('pointercancel', dropTouch);

window.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  const step = 0.06 * Math.max(0.25, state.tDist - 1);
  let hit = true;
  switch (e.key) {
    case 'ArrowLeft':  state.tLon -= step / Math.max(Math.cos(state.tLat), 0.25); break;
    case 'ArrowRight': state.tLon += step / Math.max(Math.cos(state.tLat), 0.25); break;
    case 'ArrowUp':    state.tLat = clamp(state.tLat + step, -89.3 * DEG, 89.3 * DEG); break;
    case 'ArrowDown':  state.tLat = clamp(state.tLat - step, -89.3 * DEG, 89.3 * DEG); break;
    case '+': case '=': zoomBy(0.82); break;
    case '-': case '_': zoomBy(1.22); break;
    case 'Escape': closeInfo(); break;
    default: hit = false;
  }
  if (hit) { e.preventDefault(); state.dirty = true; hideHint(); }
});

/* ------------------------------------------------------------------ ui */
const LAYERS = ['Satellite', 'Biomes', 'Ecoregions', 'Climate', 'Realms', 'Protection'];
const GROUP_SHORT = { M: 'Mamm', B: 'Bird', R: 'Rept', A: 'Amph', F: 'Fish', I: 'Invert', P: 'Plant' };
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const fmtN = n => n.toLocaleString('en-US');

function hideTip() { $('tip').classList.remove('on'); }
function hideHint() { $('hint').classList.add('hide'); }

/* ---- layer buttons ---- */
function buildLayers() {
  const g = $('lgrid');
  LAYERS.forEach((name, i) => {
    const b = document.createElement('button');
    b.className = 'lbtn' + (i === state.mode ? ' on' : '');
    b.textContent = name;
    b.onclick = () => setMode(i);
    g.appendChild(b);
  });
}
function setMode(i) {
  state.mode = i;
  [...$('lgrid').children].forEach((b, j) => b.classList.toggle('on', j === i));
  buildLegend();
  state.dirty = true;
}

/* ---- legend ---- */
function buildLegend() {
  const el = $('legend');
  const rows = [];   // [colour, label] or ['--', heading]
  const m = state.mode;
  if (m === 1) {
    rows.push(['--', 'Land']);
    Object.keys(R.biota.biomes).sort((a, b) => a - b).forEach(k => {
      const b = R.biota.biomes[k];
      rows.push([b.color, b.short]);
    });
    rows.push(['--', 'Sea']);
    Object.entries(R.biota.marine.biomes).forEach(([name, b]) => rows.push([b.color, name]));
  } else if (m === 3) {
    const kc = R.meta.koppenColors, kn = R.meta.koppenNames, ks = R.meta.koppen;
    rows.push(['--', 'Köppen-Geiger (land only)']);
    for (let i = 1; i < kc.length; i++) rows.push([kc[i], ks[i] + ' · ' + kn[i]]);
  } else if (m === 4) {
    rows.push(['--', 'Land']);
    Object.keys(REALM_COLOR).forEach(k => {
      const r = R.biota.realms[k];
      if (r) rows.push([REALM_COLOR[k], r.name]);
    });
    rows.push(['--', 'Sea']);
    Object.entries(R.biota.marine.realmColors).forEach(([name, c]) => rows.push([c, name]));
  } else if (m === 5) {
    rows.push(['--', 'Land only']);
    rows.push([NNH_COLOR[1], 'Half or more protected']);
    rows.push([NNH_COLOR[2], 'Nature could reach half']);
    rows.push([NNH_COLOR[3], 'Nature could recover']);
    rows.push([NNH_COLOR[4], 'Nature imperilled']);
  }
  if (!rows.length) { el.classList.remove('on'); return; }
  el.innerHTML = '<div class="ltitle">' + esc(LAYERS[m]) + '</div>' +
    rows.map(r => r[0] === '--'
      ? `<div class="lgsep">${esc(r[1])}</div>`
      : `<div class="lgrow"><i style="background:${esc(r[0])}"></i><span>${esc(r[1])}</span></div>`
    ).join('');
  el.classList.add('on');
}

/* ---- hover tooltip ---- */
let hoverQueued = false;
function queueHover() { hoverQueued = true; }
function doHover() {
  hoverQueued = false;
  if (!lastPointer || drag) return;
  const p = rayPick(lastPointer.x, lastPointer.y);
  const tip = $('tip');
  if (!p) {
    hideTip();
    if (state.hover || state.hoverSea) { state.hover = state.hoverSea = 0; state.dirty = true; }
    return;
  }
  const idx = ecoAt(p.lat, p.lon);
  const sea = idx ? 0 : seaAt(p.lat, p.lon);
  if (idx !== state.hover || sea !== state.hoverSea) {
    state.hover = idx; state.hoverSea = sea; state.dirty = true;
  }
  if (!idx) {
    if (!sea) { hideTip(); return; }
    const u = R.marineMeta.units[sea - 1];
    tip.innerHTML = `<b>${esc(u.name)}</b><span>${esc(u.biome)} · ${esc(u.realm)}</span>`;
    placeTip();
    return;
  }
  const e = R.meta.ecoregions[idx - 1];
  const b = R.biota.biomes[String(e.biome)];
  const cl = climateAt(p.lat, p.lon);
  tip.innerHTML = `<b>${esc(e.name)}</b><span>${esc(b ? b.short : 'Rock & ice')}` +
    (cl ? ` · ${esc(R.meta.koppen[cl.koppen])} ${cl.temp.toFixed(0)}°C` : '') + `</span>`;
  placeTip();
}

function placeTip() {
  const tip = $('tip'), r = canvas.getBoundingClientRect();
  tip.classList.add('on');
  let x = lastPointer.x + 16, y = lastPointer.y + 16;
  if (x + tip.offsetWidth > r.width - 8) x = lastPointer.x - tip.offsetWidth - 16;
  if (y + tip.offsetHeight > r.height - 8) y = lastPointer.y - tip.offsetHeight - 16;
  tip.style.left = x + 'px'; tip.style.top = y + 'px';
}

/* ---- info panel ---- */
function closeInfo() {
  $('info').classList.remove('on');
  state.sel = 0; state.selSea = 0; state.dirty = true;
}
$('iclose').onclick = closeInfo;

function selectAt(cx, cy) {
  const p = rayPick(cx, cy);
  if (!p) return closeInfo();
  const idx = ecoAt(p.lat, p.lon);
  if (idx) return showInfo(idx, p.lat, p.lon);
  const m = seaAt(p.lat, p.lon);
  if (m) return showSea(m);
  closeInfo();
}

/** Panel for a marine ecoregion or pelagic province. */
function showSea(mi) {
  const u = R.marineMeta.units[mi - 1];
  const mb = R.biota.marine.biomes[u.biome];
  const prov = R.biota.marine.provinces[u.province];
  const realm = R.biota.marine.realms[u.realm];

  state.sel = 0; state.selSea = mi; state.dirty = true;
  $('iname').textContent = u.name;

  const tags = [
    `<span class="tag"><i style="background:${esc(mb ? mb.color : '#3a63c0')}"></i>${esc(u.biome)}</span>`,
    `<span class="tag"><i style="background:${esc(R.biota.marine.realmColors[u.realm] || '#3a63c0')}"></i>${esc(u.realm)}</span>`,
    `<span class="tag">${u.type === 'PPOW' ? 'Open ocean' : 'Coastal &amp; shelf'}</span>`,
  ];
  $('imeta').innerHTML = tags.join('');

  const parts = [];
  const stats = [];
  if (u.areaKm2) stats.push([`${fmtN(u.areaKm2)} km²`, 'Area']);
  if (u.province !== u.name) stats.push([esc(u.province), 'Province', true]);
  if (stats.length) {
    parts.push('<div class="sect"><div class="sh">Marine region</div><div class="stats">' +
      stats.map(x => `<div class="stat${x[2] ? ' wide' : ''}"><b>${x[0]}</b><span>${esc(x[1])}</span></div>`).join('') +
      '</div></div>');
  }
  if (prov && prov.about) {
    parts.push(`<div class="sect"><div class="sh">${esc(prov.title)}</div><div class="about">${esc(prov.about)}</div></div>`);
  }
  if (mb && mb.about) {
    parts.push(`<div class="sect"><div class="sh">About this marine biome</div><div class="about">${esc(mb.about)}</div></div>`);
  }
  const sp = (prov && prov.species) || (realm && realm.species);
  if (sp && sp.length) {
    parts.push('<div class="sect"><div class="sh">Characteristic species</div>' + speciesHtml(sp) + '</div>');
  }
  if (realm && realm.about) {
    parts.push(`<div class="sect"><div class="sh">${esc(u.realm)} realm</div><div class="about">${esc(realm.about)}</div></div>`);
  }
  $('ibody').innerHTML = parts.join('');
  $('ibody').scrollTop = 0;
  $('info').classList.add('on');
}

/** Species grid. Photos are hotlinked Wikimedia Commons thumbnails, loaded
 *  lazily and credited to their author on hover. */
function speciesHtml(list) {
  if (!list || !list.length) return '';
  const cards = list.map(sp => {
    const im = R.images[sp[1]];
    const chip = `<span class="g g-${esc(sp[2])}">${esc(GROUP_SHORT[sp[2]] || sp[2])}</span>`;
    const pic = im
      ? `<img loading="lazy" decoding="async" src="${esc(im.u)}" alt="${esc(sp[0])}" ` +
        `title="${esc(sp[0])} — photo by ${esc(im.a || 'unknown')} (${esc(im.l)}), Wikimedia Commons">`
      : `<div class="noimg">${esc(GROUP_SHORT[sp[2]] || '?')}</div>`;
    return `<figure class="spc">${pic}${chip}` +
      `<figcaption><b>${esc(sp[0])}</b><i>${esc(sp[1])}</i></figcaption></figure>`;
  }).join('');
  return `<div class="spgrid">${cards}</div>` +
    `<div class="credit">${list.length} species · photos from Wikimedia Commons, ` +
    `hover for author and licence</div>`;
}

/** Some realm+biome codes span disjoint regions; pick the one holding this point. */
function pickCode(key, lat, lon) {
  const c = R.biota.codes[key];
  if (!c || !c.variants || lat === undefined) return c;
  const la = lat / DEG;
  let lo = lon / DEG;
  while (lo > 180) lo -= 360;
  while (lo < -180) lo += 360;
  for (const v of c.variants) {
    const b = v.box;
    if (lo >= b[0] && lo <= b[1] && la >= b[2] && la <= b[3]) return v;
  }
  return c;
}

function showInfo(idx, lat, lon) {
  const e = R.meta.ecoregions[idx - 1];
  const biome = R.biota.biomes[String(e.biome)];
  const realmKey = e.code ? e.code.slice(0, 2) : '';
  const realm = R.biota.realms[realmKey];
  const code = pickCode(e.code, lat, lon);
  const cl = (lat !== undefined) ? climateAt(lat, lon) : null;

  const bare = e.biome === 0;
  state.sel = idx; state.selSea = 0; state.dirty = true;
  $('iname').textContent = bare ? 'Rock & ice' : e.name;

  const tags = [];
  if (bare) tags.push('<span class="tag"><i style="background:#cfe3ee"></i>Permanent ice or bare rock</span>');
  if (biome) tags.push(`<span class="tag"><i style="background:${esc(biome.color)}"></i>${esc(biome.short)}</span>`);
  if (realm) tags.push(`<span class="tag"><i style="background:${esc(REALM_COLOR[realmKey] || '#777')}"></i>${esc(realm.name)}</span>`);
  if (e.nnhName && e.nnhName !== 'N/A')
    tags.push(`<span class="tag"><i style="background:${esc(NNH_COLOR[e.nnh] || '#777')}"></i>${esc(e.nnhName)}</span>`);
  $('imeta').innerHTML = tags.join('');

  const parts = [];
  const kIdx = cl ? cl.koppen : (e.koppen ? R.meta.koppen.indexOf(e.koppen) : 0);
  const stats = [];
  if (cl) {
    stats.push([`${cl.temp.toFixed(1)}°C`, 'Mean temp']);
    stats.push([`${fmtN(Math.round(cl.precip))} mm`, 'Annual rain']);
    stats.push([`${cl.tCold.toFixed(1)}°C`, 'Coldest month']);
    stats.push([`${cl.tHot.toFixed(1)}°C`, 'Warmest month']);
  } else if (e.tempC !== undefined) {
    stats.push([`${e.tempC.toFixed(1)}°C`, 'Mean temp']);
    stats.push([`${fmtN(e.precipMm)} mm`, 'Annual rain']);
  }
  if (e.areaKm2 && !bare) stats.push([`${fmtN(e.areaKm2)} km²`, 'Ecoregion area']);
  if (kIdx > 0) stats.push([`${esc(R.meta.koppen[kIdx])} · ${esc(R.meta.koppenNames[kIdx])}`, 'Köppen climate', true]);

  if (stats.length) {
    parts.push('<div class="sect"><div class="sh">Climate at this point</div><div class="stats">' +
      stats.map(s => `<div class="stat${s[2] ? ' wide' : ''}"><b>${s[0]}</b><span>${esc(s[1])}</span></div>`).join('') +
      '</div></div>');
  }
  if (bare) {
    parts.push('<div class="sect"><div class="sh">Beyond the ecoregions</div><div class="about">' +
      'Permanently glaciated or bare-rock surface — the Antarctic and Greenland ice sheets and the ' +
      'world&rsquo;s high mountain glaciers. It sits outside the ecoregion system because it carries no ' +
      'plant community of its own; what lives here comes in from the sea or the valleys below.' +
      '</div></div>');
  }
  if (code && code.about) {
    parts.push(`<div class="sect"><div class="sh">${esc(code.title)}</div><div class="about">${esc(code.about)}</div></div>`);
  }
  if (biome && biome.about) {
    parts.push(`<div class="sect"><div class="sh">About this biome</div><div class="about">${esc(biome.about)}</div></div>`);
  }
  if (code && code.species && code.species.length) {
    parts.push('<div class="sect"><div class="sh">Characteristic species</div>' +
      speciesHtml(code.species) + '</div>');
  }
  if (realm && realm.about) {
    parts.push(`<div class="sect"><div class="sh">${esc(realm.name)} realm</div><div class="about">${esc(realm.about)}</div></div>`);
  }
  $('ibody').innerHTML = parts.join('');
  $('ibody').scrollTop = 0;
  $('info').classList.add('on');
}

/* ---- search ---- */
const PLACES = [
  ['Amazon rainforest',-3.5,-62],['Serengeti',-2.3,34.8],['Sahara',23,10],['Himalaya',28,86.9],
  ['Great Barrier Reef',-18.5,147.6],['Galápagos',-0.6,-90.4],['Madagascar',-19,46.8],
  ['Borneo',0.9,114.2],['Congo Basin',0.5,22],['Okavango Delta',-19.3,22.9],['Pantanal',-17.7,-57.4],
  ['Yellowstone',44.6,-110.5],['Everglades',25.8,-80.9],['Patagonia',-49,-72.5],['Atacama',-24,-69.3],
  ['Siberia',62,100],['Gobi Desert',43,105],['Tibetan Plateau',33,88],['Sundarbans',21.9,89.2],
  ['Great Rift Valley',0.3,36],['Namib Desert',-24.5,15.3],['Kalahari',-23,21.5],['Outback',-24,133],
  ['Tasmania',-42,146.5],['New Zealand',-43.5,170.5],['Iceland',64.9,-19],['Svalbard',78.2,15.6],
  ['Greenland',72,-40],['Alaska',64,-152],['Rocky Mountains',39.5,-106],['Appalachians',36.5,-82],
  ['Great Plains',41,-100],['Mojave Desert',35.2,-116],['Costa Rica',10,-84],['Andes',-13,-72],
  ['Cerrado',-15,-49.7],['Atlantic Forest',-22.5,-43.5],['Cape Town fynbos',-33.9,18.6],
  ['Ethiopian Highlands',9.5,39.5],['Mediterranean',40,15],['Alps',46.5,10],['Scandinavia',63,15],
  ['Ural Mountains',60,59],['Caucasus',43,43],['Ganges Delta',23.5,89],['Western Ghats',12,75.6],
  ['Thar Desert',27,71.5],['Mekong Delta',10,105.8],['Sumatra',-0.5,101.5],['Java',-7.3,110],
  ['Papua New Guinea',-6,144],['Philippines',12,122],['Japan',36,138],['Korea',37,127.8],
  ['Mongolia',47,104],['Kamchatka',56,159],['Arabian Peninsula',22,45],['Red Sea coast',20,38],
  ['Nile Delta',31,31],['Sahel',15,5],['Zanzibar',-6.2,39.3],['Victoria Falls',-17.9,25.9],
  ['Great Lakes',45.5,-84],['Baja California',27,-113],['Yucatán',19.5,-89],['Hawaii',19.6,-155.5],
  ['Fiji',-17.8,178],['Antarctic Peninsula',-65,-62],['Bering Strait',65.5,-169],
  // open water
  ['Sargasso Sea',30,-55],['Coral Triangle',-4.5,126.5],['Mariana Trench',11.35,142.2],
  ['Gulf of Mexico',25,-90],['North Sea',56,3],['Baltic Sea',58,20],['Arabian Sea',15,65],
  ['Bay of Bengal',15,88],['Sea of Japan',40,135],['Bering Sea',58.5,-172],['Barents Sea',74,40],
  ['Ross Sea',-75,175],['Weddell Sea',-70,-40],['Drake Passage',-58,-63],['Tasman Sea',-40,160],
  ['Caribbean Sea',15,-75],['Coral Sea',-16,153],['Sea of Okhotsk',55,150],['Persian Gulf',27,51],
  ['Gulf of Aden',12.5,47],['Mozambique Channel',-18,41],['Scotia Sea',-57,-45]
];
let searchIdx = null, selRow = -1;
function buildSearch() {
  searchIdx = [];
  R.meta.ecoregions.forEach((e, i) => {
    if (!e.name || e.name === 'Rock and Ice') return;
    const b = R.biota.biomes[String(e.biome)];
    searchIdx.push({ n: e.name, sub: b ? b.short : '', lat: e.lat, lon: e.lon, idx: i + 1, w: 0 });
  });
  R.marineMeta.units.forEach((u, i) => {
    if (u.lat === undefined) return;
    searchIdx.push({ n: u.name, sub: u.type === 'PPOW' ? 'Open ocean' : 'Sea',
                     lat: u.lat, lon: u.lon, idx: 0, sea: i + 1, w: 0 });
  });
  // A curated place is only useful where no region already carries that name,
  // otherwise the loose coordinate would outrank the real region.
  const known = new Set(searchIdx.map(s => s.n.toLowerCase()));
  PLACES.forEach(p => {
    if (known.has(p[0].toLowerCase())) return;
    searchIdx.push({ n: p[0], sub: 'Place', lat: p[1], lon: p[2], idx: 0, w: -0.5 });
  });
  searchIdx.forEach(s => { s.lc = s.n.toLowerCase(); });
}
function runSearch(q) {
  const box = $('results');
  q = q.trim().toLowerCase();
  if (q.length < 2) { box.classList.remove('on'); return; }
  const hits = [];
  for (const s of searchIdx) {
    const at = s.lc.indexOf(q);
    if (at < 0) continue;
    hits.push({ s, score: at + s.w + (at === 0 ? -3 : 0) });
    if (hits.length > 400) break;
  }
  hits.sort((a, b) => a.score - b.score || a.s.n.length - b.s.n.length);
  const top = hits.slice(0, 12);
  if (!top.length) { box.classList.remove('on'); return; }
  selRow = -1;
  box.innerHTML = top.map((h, i) => {
    const e = h.s.idx ? R.meta.ecoregions[h.s.idx - 1] : null;
    const b = e ? R.biota.biomes[String(e.biome)] : null;
    let col = '#5fd3a6';
    if (b) col = b.color;
    else if (h.s.sea) {
      const mb = R.biota.marine.biomes[R.marineMeta.units[h.s.sea - 1].biome];
      col = mb ? mb.color : '#3aa7f0';
    }
    return `<div class="rrow" data-i="${i}"><i class="chip" style="background:${esc(col)}"></i>` +
      `<span class="nm">${esc(h.s.n)}</span><span class="sub">${esc(h.s.sub)}</span></div>`;
  }).join('');
  [...box.children].forEach((el, i) => {
    el.onmousedown = ev => { ev.preventDefault(); goTo(top[i].s); };
  });
  box.classList.add('on');
  box._top = top;
}
function goTo(s) {
  $('results').classList.remove('on');
  $('search').blur();
  let dl = s.lon * DEG - state.tLon;
  while (dl > Math.PI) dl -= 2 * Math.PI;
  while (dl < -Math.PI) dl += 2 * Math.PI;
  state.tLon += dl;
  state.tLat = clamp(s.lat * DEG, -89.3 * DEG, 89.3 * DEG);
  state.tDist = Math.min(state.tDist, 1.85);
  state.vLat = state.vLon = 0;
  state.dirty = true;
  hideHint();
  if (s.sea) { showSea(s.sea); return; }
  const lat = s.lat * DEG, lon = s.lon * DEG;
  if (s.idx) { showInfo(s.idx, lat, lon); return; }
  // A place name is just a coordinate: resolve whatever actually lies under it.
  const hit = ecoAt(lat, lon);
  if (hit) {
    const e = R.meta.ecoregions[hit - 1];
    showInfo(e.biome > 0 ? hit : ecoNear(lat, lon), lat, lon);
    return;
  }
  const m = seaAt(lat, lon);
  if (m) showSea(m); else closeInfo();
}
$('search').addEventListener('input', e => runSearch(e.target.value));
$('search').addEventListener('keydown', e => {
  const box = $('results');
  if (!box.classList.contains('on')) return;
  const rows = [...box.children];
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault();
    selRow = clamp(selRow + (e.key === 'ArrowDown' ? 1 : -1), 0, rows.length - 1);
    rows.forEach((r, i) => r.classList.toggle('sel', i === selRow));
  } else if (e.key === 'Enter') {
    e.preventDefault();
    goTo(box._top[Math.max(0, selRow)].s);
  } else if (e.key === 'Escape') { box.classList.remove('on'); $('search').blur(); }
});
document.addEventListener('click', e => {
  if (!$('searchwrap').contains(e.target)) $('results').classList.remove('on');
});

$('opacity').addEventListener('input', e => { state.opacity = e.target.value / 100; state.dirty = true; });
$('tRelief').addEventListener('change', e => { state.relief = e.target.checked ? 1 : 0; state.dirty = true; });
$('tSpin').addEventListener('change', e => { state.spin = e.target.checked; state.dirty = true; });
$('tFps').addEventListener('change', e => { state.showFps = e.target.checked; $('fps').classList.toggle('on', state.showFps); });

/* -------------------------------------------------------------- render */
let PG, PA, PB, vaoSphere, vaoQuad, sphereCount;

function initGL() {
  PG = program(VS_GLOBE, FS_GLOBE);
  PA = program(VS_GLOBE, FS_ATMO);
  PB = program(VS_BG, FS_BG);

  const s = buildSphere(192, 384);
  sphereCount = s.count;
  vaoSphere = gl.createVertexArray();
  gl.bindVertexArray(vaoSphere);
  const vb = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, vb);
  gl.bufferData(gl.ARRAY_BUFFER, s.pos, gl.STATIC_DRAW);
  gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
  const ub = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, ub);
  gl.bufferData(gl.ARRAY_BUFFER, s.uv, gl.STATIC_DRAW);
  gl.enableVertexAttribArray(1); gl.vertexAttribPointer(1, 2, gl.FLOAT, false, 0, 0);
  const ib = gl.createBuffer();
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib);
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, s.idx, gl.STATIC_DRAW);

  vaoQuad = gl.createVertexArray();
  gl.bindVertexArray(vaoQuad);
  const qb = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, qb);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
  gl.bindVertexArray(null);
}

function bindTex(unit, tex, loc) {
  gl.activeTexture(gl.TEXTURE0 + unit);
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.uniform1i(loc, unit);
}

function render() {
  const b = camBasis();
  const near = Math.max(0.002, (state.dist - 1) * 0.22);
  const proj = M4.perspective(2 * Math.atan(tanHalf()), aspect(), near, state.dist + 3);
  const view = M4.lookAt(b.eye, [0, 0, 0], [0, 1, 0]);
  const vp = M4.mul(proj, view);

  const d = state.dist;
  let L = [b.eye[0] + b.right[0] * 0.62 * d + b.up[0] * 0.34 * d,
           b.eye[1] + b.right[1] * 0.62 * d + b.up[1] * 0.34 * d,
           b.eye[2] + b.right[2] * 0.62 * d + b.up[2] * 0.34 * d];
  const ll = Math.hypot(L[0], L[1], L[2]); L = [L[0] / ll, L[1] / ll, L[2] / ll];

  gl.viewport(0, 0, canvas.width, canvas.height);
  gl.disable(gl.BLEND);
  gl.enable(gl.DEPTH_TEST); gl.depthMask(true); gl.depthFunc(gl.LEQUAL);
  gl.enable(gl.CULL_FACE); gl.cullFace(gl.BACK);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  /* globe first, so the star shader is depth-rejected behind it */
  gl.useProgram(PG.p);
  gl.uniformMatrix4fv(PG.u.uVP, false, vp);
  gl.uniform1f(PG.u.uScale, 1);
  gl.uniform3fv(PG.u.uCam, b.eye);
  gl.uniform3fv(PG.u.uLight, L);
  gl.uniform1i(PG.u.uMode, state.mode);
  gl.uniform1f(PG.u.uOpacity, state.opacity);
  gl.uniform1f(PG.u.uReliefAmt, state.relief);
  gl.uniform1i(PG.u.uHiIdx, state.hover || state.sel);
  gl.uniform1i(PG.u.uHiSea, state.hoverSea || state.selSea);
  gl.uniform2f(PG.u.uEcoSize, R.eco.w, R.eco.h);
  gl.uniform2f(PG.u.uClimSize, R.climA.w, R.climA.h);
  gl.uniform2f(PG.u.uReliefSize, R.reliefW, R.reliefH);
  bindTex(0, R.texBase, PG.u.uBase);
  bindTex(1, R.eco.tex, PG.u.uEco);
  bindTex(5, R.marine.tex, PG.u.uMarine);
  bindTex(2, R.texClim, PG.u.uClim);
  bindTex(3, R.texRelief, PG.u.uRelief);
  bindTex(4, R.texLut, PG.u.uLut);
  gl.bindVertexArray(vaoSphere);
  gl.drawElements(gl.TRIANGLES, sphereCount, gl.UNSIGNED_INT, 0);

  /* stars, only where the globe left the depth buffer at the far plane */
  gl.depthMask(false); gl.disable(gl.CULL_FACE);
  gl.useProgram(PB.p);
  gl.uniform3fv(PB.u.uRight, b.right); gl.uniform3fv(PB.u.uUp, b.up); gl.uniform3fv(PB.u.uFwd, b.fwd);
  gl.uniform1f(PB.u.uTanHalf, tanHalf()); gl.uniform1f(PB.u.uAspect, aspect());
  gl.bindVertexArray(vaoQuad);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  gl.enable(gl.CULL_FACE);

  /* atmosphere halo: back faces of a slightly larger shell */
  gl.bindVertexArray(vaoSphere);
  gl.useProgram(PA.p);
  gl.uniformMatrix4fv(PA.u.uVP, false, vp);
  gl.uniform1f(PA.u.uScale, 1.028);
  gl.uniform3fv(PA.u.uCam, b.eye);
  gl.uniform3fv(PA.u.uLight, L);
  gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
  gl.cullFace(gl.FRONT);
  gl.drawElements(gl.TRIANGLES, sphereCount, gl.UNSIGNED_INT, 0);
  gl.cullFace(gl.BACK); gl.depthMask(true); gl.disable(gl.BLEND);
  gl.bindVertexArray(null);
}

function resize() {
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
  const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w; canvas.height = h; state.dirty = true;
  }
}
window.addEventListener('resize', resize);
/* Catches container-driven size changes the window event never reports
   (panes, iframes, a tab that starts out hidden). */
if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas);

let lastT = 0, fpsT = 0, fpsN = 0, lastRender = -1e9;
function frame(t) {
  requestAnimationFrame(frame);
  const dt = Math.min(60, t - lastT) || 16.7;
  lastT = t;
  const k = 1 - Math.pow(1 - 0.17, dt / 16.67);

  if (state.spin && !drag) { state.tLon += 0.00011 * dt; state.dirty = true; }

  if (!drag && (state.vLon || state.vLat)) {
    state.tLon += state.vLon;
    state.tLat = clamp(state.tLat + state.vLat, -89.3 * DEG, 89.3 * DEG);
    const decay = Math.pow(0.90, dt / 16.67);
    state.vLon *= decay; state.vLat *= decay;
    if (Math.abs(state.vLon) < 2e-6) state.vLon = 0;
    if (Math.abs(state.vLat) < 2e-6) state.vLat = 0;
    state.dirty = true;
  }

  const dLon = state.tLon - state.lon, dLat = state.tLat - state.lat, dD = state.tDist - state.dist;
  if (Math.abs(dLon) > 1e-7 || Math.abs(dLat) > 1e-7 || Math.abs(dD) > 1e-7) {
    state.lon += dLon * k; state.lat += dLat * k; state.dist += dD * k;
    state.dirty = true;
  } else if (dLon || dLat || dD) {
    state.lon = state.tLon; state.lat = state.tLat; state.dist = state.tDist;
    state.dirty = true;
  }
  if (state.lon > 12.57) { state.lon -= 12.566370614; state.tLon -= 12.566370614; }
  else if (state.lon < -12.57) { state.lon += 12.566370614; state.tLon += 12.566370614; }

  if (hoverQueued) doHover();

  if (state.dirty) {
    state.dirty = false;
    render();
    if (state.showFps) {
      if (t - lastRender > 200) { fpsT = t; fpsN = 0; }   // start a fresh burst
      lastRender = t;
      fpsN++;
      if (t - fpsT > 500) {
        $('fps').textContent = Math.round(fpsN * 1000 / (t - fpsT)) + ' fps';
        fpsT = t; fpsN = 0;
      }
    }
  } else if (state.showFps && t - lastRender > 400) {
    $('fps').textContent = 'idle';
  }
}

/* ---------------------------------------------------------------- boot */
async function boot() {
  const msgs = ['Loading ecoregions…', 'Loading species…', 'Loading imagery…',
                'Mapping the land…', 'Mapping the sea…', 'Loading climate…',
                'Building the globe…'];
  let done = 0;
  const tick = () => {
    $('lfill').style.width = Math.round(++done / 7 * 100) + '%';
    if (msgs[done]) $('lmsg').textContent = msgs[done];
  };
  const grab = (p) => p.then(v => { tick(); return v; });

  try {
    const [meta, biota, marineMeta, images, baseImg, ecoPx, marinePx, climA, climB, relief] =
      await Promise.all([
        grab(fetch(url('ecoregions.json')).then(r => r.json())),
        grab(fetch(url('biota.json')).then(r => r.json())),
        fetch(url('marine.json')).then(r => r.json()),
        fetch(url('species_images.json')).then(r => r.json()).catch(() => ({})),
        grab(loadImage(url('basemap.jpg'))),
        grab(decodePng(url('ecoregions.png'))),
        grab(decodePng(url('marine.png'))),
        grab(decodePng(url('climate_a.png'))),
        decodePng(url('climate_b.png')),
        decodePng(url('relief.png'))
      ]);
    $('lmsg').textContent = 'Building the globe…';
    $('lfill').style.width = '100%';

    for (const [obj, key, what] of [[meta, 'koppenColors', 'ecoregions.json'],
                                    [biota, 'marine', 'biota.json'],
                                    [marineMeta, 'units', 'marine.json']]) {
      if (!obj || !obj[key]) throw new Error(`${what} is missing "${key}" — rebuild data (build/build_all.sh) or bump DATA_VERSION`);
    }

    initGL();
    R = {
      meta, biota, images, climA, climB,
      marineMeta,
      eco: indexRaster(ecoPx),
      marine: indexRaster(marinePx),
      texBase: texFromImage(baseImg),
      texClim: texFromPixels(climA.px, climA.w, climA.h, gl.NEAREST),
      texRelief: texRelief(relief),
      reliefW: relief.w, reliefH: relief.h
    };
    R.texLut = buildLut(meta, marineMeta, biota);

    buildLayers();
    buildLegend();
    buildSearch();
    resize();
    state.tDist = aspect() < 0.85 ? 2.45 : 2.9;
    requestAnimationFrame(frame);
    setTimeout(() => $('loader').classList.add('done'), 120);
    setTimeout(() => $('loader').style.display = 'none', 800);
    setTimeout(hideHint, 11000);
  } catch (err) {
    console.error(err);
    $('lmsg').innerHTML = 'Could not load the globe data.<br><span style="font-size:11px">' +
      esc(err.message || err) + '</span>';
    document.querySelector('.lring').style.display = 'none';
  }
}
boot();
})();
