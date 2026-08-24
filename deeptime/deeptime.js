/* Deep Time - 4.6 billion years of Earth, driven by the page scroll.
 *
 * The globe is not a slideshow of pre-rendered maps.  It holds one copy of the
 * present-day coastlines, each polygon tagged with the tectonic plate it rides
 * on, and every frame it slerps that plate's rotation to the current age and
 * spins the vertices into place.  Continental drift is therefore continuous:
 * scrolling half a chapter moves the continents half as far.
 *
 * Dependency-free WebGL2.  Data: Muller et al. (2025) plate model, the
 * Paleobiology Database, and the compilations cited in chapters.json.
 */
(() => {
'use strict';

/* Bump when anything in data/ is rebuilt - these files are cached hard. */
const DATA_VERSION = '3';
const url = f => `data/${f}?v=${DATA_VERSION}`;
const $ = id => document.getElementById(id);
const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const DEG = Math.PI / 180;

/* Markers are coloured by the dominant group at each locality; the order
   matches GROUPS in build/fossils.py, with "Other" last. */
const GROUP_COLOR = [
  [0.98, 0.62, 0.28], [0.44, 0.80, 0.94], [0.78, 0.62, 0.96], [0.42, 0.86, 0.68],
  [0.98, 0.45, 0.52], [0.99, 0.83, 0.36], [0.62, 0.72, 0.98], [0.96, 0.55, 0.80],
  [0.72, 0.86, 0.46], [0.36, 0.82, 0.52], [0.60, 0.88, 0.86], [0.86, 0.74, 0.55],
  [0.62, 0.66, 0.74],
];
const css = c => `rgb(${c.map(v => Math.round(v * 255)).join(',')})`;
const hexRGB = h => [parseInt(h.slice(1, 3), 16) / 255,
                     parseInt(h.slice(3, 5), 16) / 255,
                     parseInt(h.slice(5, 7), 16) / 255];
/** Lift a chapter colour toward white so a ring drawn on land still reads. */
const ringTint = h => hexRGB(h).map(v => v + (1 - v) * 0.5);

/* ------------------------------------------------------------------- maths */
const M4 = {
  perspective(fovy, aspect, near, far) {
    const f = 1 / Math.tan(fovy / 2), nf = 1 / (near - far);
    return new Float32Array([f / aspect,0,0,0, 0,f,0,0, 0,0,(far+near)*nf,-1, 0,0,2*far*near*nf,0]);
  },
  mul(a, b) {
    const o = new Float32Array(16);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
      let s = 0;
      for (let k = 0; k < 4; k++) s += a[k * 4 + r] * b[c * 4 + k];
      o[c * 4 + r] = s;
    }
    return o;
  },
};

/** Rotate v by unit quaternion q (w,x,y,z). */
function qrot(q, v) {
  const [w, x, y, z] = q, [a, b, c] = v;
  const tx = 2 * (y * c - z * b), ty = 2 * (z * a - x * c), tz = 2 * (x * b - y * a);
  return [a + w * tx + y * tz - z * ty,
          b + w * ty + z * tx - x * tz,
          c + w * tz + x * ty - y * tx];
}

/* ----------------------------------------------------------------- shaders */
const COMMON = `
/* Where the fragment sits on the globe, and whether we can see it at all.
   The horizon test is exact per-fragment, which keeps big triangles from
   spilling past the limb without needing a depth buffer. */
float horizon(vec3 p, vec3 eye, float dist){
  return dot(normalize(p), eye) - 1.0 / dist;
}
float latitude(vec3 p){ return degrees(asin(clamp(normalize(p).z, -1.0, 1.0))); }

float hash13(vec3 p){
  p = fract(p * 0.3183099 + vec3(0.71, 0.113, 0.419));
  p *= 17.0;
  return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}
float vnoise(vec3 x){
  vec3 i = floor(x), f = fract(x);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(mix(hash13(i + vec3(0,0,0)), hash13(i + vec3(1,0,0)), f.x),
                 mix(hash13(i + vec3(0,1,0)), hash13(i + vec3(1,1,0)), f.x), f.y),
             mix(mix(hash13(i + vec3(0,0,1)), hash13(i + vec3(1,0,1)), f.x),
                 mix(hash13(i + vec3(0,1,1)), hash13(i + vec3(1,1,1)), f.x), f.y), f.z);
}
float fbm(vec3 p){
  float s = 0.0, a = 0.5;
  for (int i = 0; i < 5; i++){ s += a * vnoise(p); p *= 2.03; a *= 0.5; }
  return s;
}
`;

/* The globe: ocean, ice and atmosphere on a plain sphere. */
const VS_SPHERE = `#version 300 es
layout(location=0) in vec3 aPos;
uniform mat4 uVP; uniform mat3 uRot;
out vec3 vP;     /* view frame: for the horizon test and the sun */
out vec3 vGeo;   /* globe frame: for latitude */
void main(){ vGeo = aPos; vP = uRot * aPos; gl_Position = uVP * vec4(vP, 1.0); }`;

const FS_SPHERE = `#version 300 es
precision highp float;
in vec3 vP; in vec3 vGeo;
out vec4 o;
uniform vec3 uEye; uniform float uDist, uIce, uSea, uHot, uMolten;
uniform vec3 uSun;
${COMMON}
void main(){
  if (horizon(vP, uEye, uDist) < 0.0) discard;
  vec3 n = normalize(vP);
  float lat = abs(latitude(vGeo));

  /* Depth-ish variation so the ocean is not a flat wash. */
  float d = fbm(vGeo * 3.4);
  vec3 deep = mix(vec3(0.055,0.115,0.235), vec3(0.085,0.175,0.315), d);
  /* Warmer worlds get slightly greener, more stratified seas. */
  deep = mix(deep, vec3(0.075,0.20,0.27), uHot * 0.5);

  float ice = smoothstep(uIce - 2.0, uIce + 13.0, lat);
  vec3 col = mix(deep, vec3(0.86,0.90,0.95), ice * 0.90);

  float lam = clamp(dot(n, uSun), 0.0, 1.0);
  col *= 0.30 + 0.82 * lam;
  /* specular glint off water only */
  vec3 h = normalize(uSun + uEye);
  col += vec3(0.5,0.6,0.7) * pow(clamp(dot(n, h), 0.0, 1.0), 60.0) * 0.35 * (1.0 - ice);
  /* atmosphere thickening toward the limb */
  float rim = pow(1.0 - clamp(dot(n, uEye), 0.0, 1.0), 3.0);
  col += vec3(0.22,0.42,0.75) * rim * (0.35 + 0.5 * lam);

  /* Before there was an ocean there was a magma one. */
  if (uMolten > 0.001){
    float m = fbm(n * 5.0);
    float crack = smoothstep(0.40, 0.66, m);
    vec3 lava = mix(vec3(0.085,0.040,0.032), vec3(0.62,0.16,0.03), crack);
    lava += vec3(1.0,0.42,0.10) * pow(crack, 4.0) * 0.85;
    lava *= 0.55 + 0.55 * lam;
    lava += vec3(0.9,0.30,0.08) * rim * 0.5;
    col = mix(col, lava, uMolten);
  }
  o = vec4(col, 1.0);
}`;

/* Land and continental shelf: rotated per plate, culled by the age each
   polygon exists for. */
const VS_LAND = `#version 300 es
layout(location=0) in vec3 aPos;      /* present-day unit vector          */
layout(location=1) in uint aFid;      /* which polygon this vertex is in  */
uniform mat4 uVP; uniform mat3 uRot;
uniform sampler2D uFeat;              /* plate index, first age, last age */
uniform sampler2D uQuat;              /* one rotation per plate, this age */
uniform float uTime, uLift;
out vec3 vP;                          /* view frame: horizon and sunlight */
out vec3 vGeo;                        /* globe frame: latitude            */
out vec3 vHome;                       /* present-day position, for terrain*/
void main(){
  ivec2 fc = ivec2(int(aFid) & 1023, int(aFid) >> 10);
  vec4 f = texelFetch(uFeat, fc, 0);
  if (uTime > f.y || uTime < f.z){    /* not around at this age */
    gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
    return;
  }
  vec4 q = texelFetch(uQuat, ivec2(int(f.x), 0), 0);
  vec3 p = normalize(aPos);
  vec3 t = 2.0 * cross(q.yzw, p);
  vHome = p;
  vGeo = p + q.x * t + cross(q.yzw, t);
  vP = uRot * (vGeo * uLift);
  gl_Position = uVP * vec4(vP, 1.0);
}`;

const FS_LAND = `#version 300 es
precision highp float;
in vec3 vP; in vec3 vGeo; in vec3 vHome;
out vec4 o;
uniform vec3 uEye, uSun;
uniform float uDist, uIce, uGreen, uShelf, uFade;
${COMMON}
void main(){
  if (horizon(vP, uEye, uDist) < 0.0) discard;
  vec3 n = normalize(vP);
  float lat = abs(latitude(vGeo));
  float ice = smoothstep(uIce - 2.0, uIce + 13.0, lat);

  if (uShelf > 0.5){                       /* flooded continental shelf */
    float d = fbm(vHome * 5.0);
    vec3 c = mix(vec3(0.09,0.24,0.35), vec3(0.13,0.33,0.44), d);
    c = mix(c, vec3(0.82,0.88,0.93), ice * 0.85);
    c *= 0.34 + 0.80 * clamp(dot(n, uSun), 0.0, 1.0);
    o = vec4(c, uFade);
    return;
  }

  /* Relief is keyed to the present-day position, so the texture travels with
     the plate rather than sliding over it. */
  float h = fbm(vHome * 7.0);
  float ridge = fbm(vHome * 18.0);

  vec3 rock  = mix(vec3(0.30,0.26,0.23), vec3(0.44,0.39,0.34), h);
  vec3 sand  = mix(vec3(0.66,0.53,0.33), vec3(0.78,0.66,0.44), ridge);
  vec3 wet   = mix(vec3(0.13,0.30,0.13), vec3(0.20,0.40,0.17), h);
  vec3 temp  = mix(vec3(0.24,0.36,0.19), vec3(0.36,0.45,0.24), ridge);
  vec3 cold  = mix(vec3(0.26,0.32,0.28), vec3(0.34,0.38,0.33), h);

  /* Climate belts by latitude, softened so the bands are not stripes. */
  float wob = (fbm(vHome * 2.2) - 0.5) * 11.0;
  float l = lat + wob;
  float fTrop = 1.0 - smoothstep(9.0, 20.0, l);
  float fArid = smoothstep(11.0, 20.0, l) * (1.0 - smoothstep(28.0, 38.0, l));
  float fTemp = smoothstep(30.0, 40.0, l) * (1.0 - smoothstep(56.0, 66.0, l));
  float fCold = smoothstep(58.0, 68.0, l);

  vec3 veg = wet * fTrop + sand * fArid + temp * fTemp + cold * fCold;
  veg /= max(fTrop + fArid + fTemp + fCold, 0.001);
  /* Arid belts stay bare even in a well-vegetated world. */
  float cover = uGreen * (1.0 - 0.55 * fArid) * (1.0 - 0.5 * fCold);
  vec3 col = mix(rock, veg, clamp(cover, 0.0, 1.0));
  col = mix(col, sand, fArid * (1.0 - uGreen) * 0.5);
  col = mix(col, vec3(0.90,0.93,0.96), ice * 0.95);

  /* Shading from the relief field, plus the sun. */
  float bump = 0.72 + 0.55 * h + 0.22 * ridge;
  col *= bump;
  col *= 0.34 + 0.84 * clamp(dot(n, uSun), 0.0, 1.0);
  o = vec4(col, uFade);
}`;

/* Fossil localities. */
const VS_PIN = `#version 300 es
layout(location=0) in vec3 aPos;
layout(location=1) in float aPlate;
layout(location=2) in float aGroup;
layout(location=3) in vec2 aAge;      /* first, last */
layout(location=4) in float aSize;
layout(location=5) in float aMatch;   /* 1 when it satisfies the search      */
uniform mat4 uVP; uniform mat3 uRot;
uniform sampler2D uQuat;
uniform float uTime, uPx, uSel, uFilter, uPulse;
uniform vec3 uEye; uniform float uDist;
uniform vec3 uGroupCol[13];
uniform float uGroupOn[13];
out vec3 vC; out float vOn; out float vSel; out float vDim; out float vHit;
${COMMON}
void main(){
  vec4 q = texelFetch(uQuat, ivec2(int(aPlate), 0), 0);
  vec3 p = normalize(aPos);
  vec3 t = 2.0 * cross(q.yzw, p);
  vec3 w = uRot * (p + q.x * t + cross(q.yzw, t));
  int g = int(aGroup);
  vOn = (uTime <= aAge.x + 0.001 && uTime >= aAge.y - 0.001 &&
         uGroupOn[g] > 0.5 && horizon(w, uEye, uDist) > 0.004) ? 1.0 : 0.0;
  vSel = (uSel > -0.5 && abs(uSel - float(gl_VertexID)) < 0.5) ? 1.0 : 0.0;
  vDim = (uFilter > 0.5 && aMatch < 0.5) ? 1.0 : 0.0;
  vHit = (uFilter > 0.5 && aMatch > 0.5) ? 1.0 : 0.0;
  vC = uGroupCol[g];
  gl_Position = uVP * vec4(w * 1.004, 1.0);
  /* A hit grows, gains a ring and breathes; everything else shrinks back so the
     answer to the search is obvious at a glance. */
  float size = aSize * (1.0 - 0.42 * vDim) * (1.0 + 0.55 * vHit)
             + vHit * (5.5 + uPulse * 1.8) + vSel * 5.0;
  gl_PointSize = (vOn > 0.5) ? size * uPx : 0.0;
}`;

const FS_PIN = `#version 300 es
precision highp float;
in vec3 vC; in float vOn; in float vSel; in float vDim; in float vHit;
out vec4 o;
void main(){
  if (vOn < 0.5) discard;
  vec2 d = gl_PointCoord - 0.5;
  float r = length(d) * 2.0;
  if (r > 1.0) discard;
  float core = 1.0 - smoothstep(0.55, 0.78, r);
  float ring = smoothstep(0.72, 0.86, r) * (1.0 - smoothstep(0.92, 1.0, r));
  vec3 c = mix(vC, vec3(1.0), 0.15 + vSel * 0.5);
  c = mix(c, vec3(dot(c, vec3(0.33))), vDim * 0.62);
  float a = (core * 0.92 + ring * (0.65 + vSel * 0.35)) * (1.0 - 0.62 * vDim);

  if (vHit > 0.5) {                       /* white halo around a search hit */
    float halo = smoothstep(0.60, 0.74, r) * (1.0 - smoothstep(0.86, 0.99, r));
    c = mix(c, vec3(1.0), halo * 0.85);
    a = max(a, halo);
    a *= 1.0;
  }
  if (a < 0.02) discard;
  o = vec4(c * (0.55 + 0.45 * core + 0.35 * vHit), a);
}`;

/* The ring that marks a searched place.  Built on the CPU each frame as a
   triangle strip so its radius can breathe; alpha peaks in the middle of the
   band, which gives it soft edges without a texture. */
const VS_RING = `#version 300 es
layout(location=0) in vec3 aPos;
layout(location=1) in float aT;
uniform mat4 uVP; uniform mat3 uRot;
out vec3 vP; out float vT;
void main(){ vT = aT; vP = uRot * aPos; gl_Position = uVP * vec4(vP * 1.006, 1.0); }`;

const FS_RING = `#version 300 es
precision highp float;
in vec3 vP; in float vT;
out vec4 o;
uniform vec3 uEye; uniform float uDist, uAlpha;
uniform vec3 uCol;
${COMMON}
void main(){
  float h = horizon(vP, uEye, uDist);
  if (h < 0.0) discard;
  float band = sin(vT * 3.14159265);
  float a = band * band * uAlpha * smoothstep(0.0, 0.05, h);
  if (a < 0.01) discard;
  o = vec4(uCol, a);
}`;

/* Latitude circles, so drift is readable against something fixed. */
const VS_GRID = `#version 300 es
layout(location=0) in vec3 aPos;
uniform mat4 uVP; uniform mat3 uRot;
out vec3 vP;
void main(){ vP = uRot * aPos; gl_Position = uVP * vec4(vP * 1.0015, 1.0); }`;

const FS_GRID = `#version 300 es
precision highp float;
in vec3 vP;
out vec4 o;
uniform vec3 uEye; uniform float uDist; uniform vec4 uCol;
${COMMON}
void main(){
  float h = horizon(vP, uEye, uDist);
  if (h < 0.0) discard;
  o = vec4(uCol.rgb, uCol.a * smoothstep(0.0, 0.05, h));
}`;

/* --------------------------------------------------------------- gl set-up */
const cv = $('gl');
const gl = cv.getContext('webgl2', { antialias: true, alpha: false, depth: false });
if (!gl) {
  $('loadmsg').textContent = 'This page needs WebGL2, which this browser does not offer.';
  return;
}

function shader(type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src); gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS))
    throw new Error(gl.getShaderInfoLog(s) + '\n' + src.split('\n').map((l, i) => i + 1 + ' ' + l).join('\n'));
  return s;
}
function program(vs, fs) {
  const p = gl.createProgram();
  gl.attachShader(p, shader(gl.VERTEX_SHADER, vs));
  gl.attachShader(p, shader(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
  p.u = new Proxy({}, { get: (c, n) => n in c ? c[n] : (c[n] = gl.getUniformLocation(p, n)) });
  return p;
}

const P = {};
const buf = {};
const tex = {};

/* --------------------------------------------------------------- app state */
const S = {
  t: 4567, ch: 0, prog: 0,
  yaw: 2.6, pitch: -0.30, zoom: 1, dist: 3.0, aspect: 1,
  spin: false, play: false, pins: true,
  sel: -1, groupOn: new Array(13).fill(1), filter: null, filterKind: null, fly: null,
  ring: null, ringCol: null,
  ready: false,
};

let CH = null;            /* chapters.json                      */
let PL = null;            /* plates.json                        */
let plateIndex = null;    /* GPlates plate id -> row in uQuat    */
let rot = null;           /* rotation sample tables              */
let quatData = null;      /* the per-plate rotation, this frame  */
let IMG = {};             /* photo lookup                        */
const chData = {};        /* per-chapter fossil files, lazily    */
let chIndex = null;       /* which chapters have one at all      */
let pins = null;          /* the marker buffer currently uploaded*/

/* ------------------------------------------------------------------ curves */
function at(points, t) {
  if (!points || !points.length) return 0;
  if (t >= points[0][0]) return points[0][1];
  const last = points[points.length - 1];
  if (t <= last[0]) return last[1];
  for (let i = 0; i < points.length - 1; i++) {
    const [a1, v1] = points[i], [a2, v2] = points[i + 1];
    if (t <= a1 && t >= a2) {
      const u = a1 === a2 ? 0 : (a1 - t) / (a1 - a2);
      return v1 + (v2 - v1) * u;
    }
  }
  return last[1];
}

/* -------------------------------------------------------------- geometries */
function sphereMesh(seg, ring) {
  const pos = [], idx = [];
  for (let j = 0; j <= ring; j++) {
    const v = j / ring, phi = v * Math.PI, sp = Math.sin(phi), cp = Math.cos(phi);
    for (let i = 0; i <= seg; i++) {
      const u = i / seg, th = u * 2 * Math.PI;
      pos.push(sp * Math.cos(th), sp * Math.sin(th), cp);
    }
  }
  for (let j = 0; j < ring; j++) for (let i = 0; i < seg; i++) {
    const a = j * (seg + 1) + i, b = a + seg + 1;
    idx.push(a, b, a + 1, b, b + 1, a + 1);
  }
  return { pos: new Float32Array(pos), idx: new Uint32Array(idx) };
}

function latCircles() {
  const pos = [], runs = [];
  for (const lat of [-60, -30, 0, 30, 60]) {
    const start = pos.length / 3, z = Math.sin(lat * DEG), r = Math.cos(lat * DEG);
    const n = 256;
    for (let i = 0; i <= n; i++) {
      const a = i / n * 2 * Math.PI;
      pos.push(r * Math.cos(a), r * Math.sin(a), z);
    }
    runs.push({ start, count: n + 1, major: lat === 0 });
  }
  return { pos: new Float32Array(pos), runs };
}

/* ------------------------------------------------------- rotation playback */
function buildRotations() {
  const s = PL.sections, b = PL.buffer;
  const view = (n, T) => new T(b, s[n].off, s[n].len);
  rot = {
    off: view('rotOff', Uint32Array),
    len: view('rotLen', Uint32Array),
    time: view('rotTime', Int16Array),
    quat: view('rotQuat', Int16Array),
  };
  quatData = new Float32Array(PL.plateCount * 4);
  plateIndex = new Map(PL.plateIds.map((id, i) => [id, i]));
}

/** Slerp every plate's rotation to age t and hand it to the GPU. */
function poseAt(t) {
  const { off, len, time, quat } = rot, q = quatData;
  for (let p = 0; p < PL.plateCount; p++) {
    const o = off[p], n = len[p];
    if (!n) { q[p * 4] = 1; q[p * 4 + 1] = q[p * 4 + 2] = q[p * 4 + 3] = 0; continue; }
    let i = 0;
    if (n > 1) {
      const half = t * 2;
      let lo = 0, hi = n - 1;
      if (half <= time[o]) { i = 0; }
      else if (half >= time[o + n - 1]) { i = n - 2; }
      else {
        while (lo < hi - 1) {
          const mid = (lo + hi) >> 1;
          if (time[o + mid] <= half) lo = mid; else hi = mid;
        }
        i = lo;
      }
    }
    const j = Math.min(i + 1, n - 1);
    const t0 = time[o + i] / 2, t1 = time[o + j] / 2;
    let u = t1 === t0 ? 0 : (t - t0) / (t1 - t0);
    u = clamp(u, 0, 1);
    const a = (o + i) * 4, c = (o + j) * 4;
    let aw = quat[a] / 32767, ax = quat[a + 1] / 32767, ay = quat[a + 2] / 32767, az = quat[a + 3] / 32767;
    let bw = quat[c] / 32767, bx = quat[c + 1] / 32767, by = quat[c + 2] / 32767, bz = quat[c + 3] / 32767;
    let d = aw * bw + ax * bx + ay * by + az * bz;
    if (d < 0) { bw = -bw; bx = -bx; by = -by; bz = -bz; d = -d; }
    let ca, cb;
    if (d > 0.9995) { ca = 1 - u; cb = u; }
    else {
      const th = Math.acos(clamp(d, -1, 1)), sn = Math.sin(th);
      ca = Math.sin((1 - u) * th) / sn; cb = Math.sin(u * th) / sn;
    }
    let w = aw * ca + bw * cb, x = ax * ca + bx * cb, y = ay * ca + by * cb, z = az * ca + bz * cb;
    const nn = Math.hypot(w, x, y, z) || 1;
    q[p * 4] = w / nn; q[p * 4 + 1] = x / nn; q[p * 4 + 2] = y / nn; q[p * 4 + 3] = z / nn;
  }
  gl.activeTexture(gl.TEXTURE1);
  gl.bindTexture(gl.TEXTURE_2D, tex.quat);
  gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, PL.plateCount, 1, gl.RGBA, gl.FLOAT, q);
}

/* --------------------------------------------------------------- gl upload */
function initGL() {
  P.sphere = program(VS_SPHERE, FS_SPHERE);
  P.land = program(VS_LAND, FS_LAND);
  P.pin = program(VS_PIN, FS_PIN);
  P.grid = program(VS_GRID, FS_GRID);
  P.ring = program(VS_RING, FS_RING);

  const sm = sphereMesh(160, 80);
  buf.sphere = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.sphere);
  gl.bufferData(gl.ARRAY_BUFFER, sm.pos, gl.STATIC_DRAW);
  buf.sphereIdx = gl.createBuffer();
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buf.sphereIdx);
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, sm.idx, gl.STATIC_DRAW);
  buf.sphereCount = sm.idx.length;

  const lc = latCircles();
  buf.grid = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.grid);
  gl.bufferData(gl.ARRAY_BUFFER, lc.pos, gl.STATIC_DRAW);
  buf.gridRuns = lc.runs;

  const s = PL.sections, b = PL.buffer;
  buf.pos = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.pos);
  gl.bufferData(gl.ARRAY_BUFFER, new Int16Array(b, s.pos.off, s.pos.len), gl.STATIC_DRAW);
  buf.fid = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.fid);
  gl.bufferData(gl.ARRAY_BUFFER, new Uint16Array(b, s.fid.off, s.fid.len), gl.STATIC_DRAW);
  buf.idx = gl.createBuffer();
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buf.idx);
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(b, s.idx.off, s.idx.len), gl.STATIC_DRAW);

  /* one texel per polygon: which plate, and the ages it exists between */
  const fp = new Uint16Array(b, s.featPlate.off, s.featPlate.len);
  const ff = new Int16Array(b, s.featFrom.off, s.featFrom.len);
  const ft = new Int16Array(b, s.featTo.off, s.featTo.len);
  const W = 1024, H = Math.ceil(fp.length / W);
  const fd = new Float32Array(W * H * 4);
  for (let i = 0; i < fp.length; i++) {
    fd[i * 4] = fp[i]; fd[i * 4 + 1] = ff[i]; fd[i * 4 + 2] = ft[i];
  }
  tex.feat = gl.createTexture();
  gl.activeTexture(gl.TEXTURE0);
  gl.bindTexture(gl.TEXTURE_2D, tex.feat);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, W, H, 0, gl.RGBA, gl.FLOAT, fd);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

  tex.quat = gl.createTexture();
  gl.activeTexture(gl.TEXTURE1);
  gl.bindTexture(gl.TEXTURE_2D, tex.quat);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, PL.plateCount, 1, 0, gl.RGBA, gl.FLOAT, null);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

  buf.pin = gl.createBuffer();
  buf.match = gl.createBuffer();
  buf.ring = gl.createBuffer();
  buf.ringT = gl.createBuffer();
  {   /* the strip alternates inner and outer edge, so t flips every vertex */
    const t = new Float32Array((RING_SEG + 1) * 2);
    for (let i = 0; i <= RING_SEG; i++) { t[i * 2] = 0; t[i * 2 + 1] = 1; }
    gl.bindBuffer(gl.ARRAY_BUFFER, buf.ringT);
    gl.bufferData(gl.ARRAY_BUFFER, t, gl.STATIC_DRAW);
  }
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
  gl.clearColor(0.027, 0.035, 0.059, 1);
}

/** Pack the current chapter's localities into the marker buffer. */
function uploadPins(d) {
  if (!d || !d.sites || !d.sites.lon.length) { pins = null; return; }
  const s = d.sites, n = s.lon.length;
  const a = new Float32Array(n * 8);
  const keep = [];
  for (let i = 0; i < n; i++) {
    const pi = plateIndex.get(s.plate[i]);
    if (pi === undefined) continue;
    const k = keep.length;
    const la = s.lat[i] * DEG, lo = s.lon[i] * DEG, c = Math.cos(la);
    a[k * 8] = c * Math.cos(lo); a[k * 8 + 1] = c * Math.sin(lo); a[k * 8 + 2] = Math.sin(la);
    a[k * 8 + 3] = pi;
    a[k * 8 + 4] = Math.min(s.g[i], 12);
    a[k * 8 + 5] = s.ea[i]; a[k * 8 + 6] = s.la[i];
    a[k * 8 + 7] = clamp(3.4 + Math.sqrt(s.n[i]) * 0.62, 3.4, 11);
    keep.push(i);
  }
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.pin);
  gl.bufferData(gl.ARRAY_BUFFER, a.subarray(0, keep.length * 8), gl.DYNAMIC_DRAW);
  const match = new Float32Array(keep.length);
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.match);
  gl.bufferData(gl.ARRAY_BUFFER, match, gl.DYNAMIC_DRAW);
  pins = { n: keep.length, map: keep, data: a, match, chapter: d.id };
}

const RING_SEG = 160;
const ringXYZ = new Float32Array((RING_SEG + 1) * 2 * 3);

/** Lay a circle of angular radius `rad` around `centre` on the unit sphere. */
function buildRing(centre, rad, width) {
  let up = [0, 0, 1];
  if (Math.abs(centre[2]) > 0.9) up = [1, 0, 0];
  let e = [up[1] * centre[2] - up[2] * centre[1],
           up[2] * centre[0] - up[0] * centre[2],
           up[0] * centre[1] - up[1] * centre[0]];
  const el = Math.hypot(e[0], e[1], e[2]) || 1;
  e = [e[0] / el, e[1] / el, e[2] / el];
  const n = [centre[1] * e[2] - centre[2] * e[1],
             centre[2] * e[0] - centre[0] * e[2],
             centre[0] * e[1] - centre[1] * e[0]];
  const r0 = Math.max(0.004, rad - width), r1 = rad + width;
  for (let i = 0; i <= RING_SEG; i++) {
    const a = i / RING_SEG * 2 * Math.PI, ca = Math.cos(a), sa = Math.sin(a);
    const dx = e[0] * ca + n[0] * sa, dy = e[1] * ca + n[1] * sa, dz = e[2] * ca + n[2] * sa;
    for (let k = 0; k < 2; k++) {
      const rr = k ? r1 : r0, c = Math.cos(rr), sn = Math.sin(rr);
      const o = (i * 2 + k) * 3;
      ringXYZ[o] = centre[0] * c + dx * sn;
      ringXYZ[o + 1] = centre[1] * c + dy * sn;
      ringXYZ[o + 2] = centre[2] * c + dz * sn;
    }
  }
  return ringXYZ;
}

/* ------------------------------------------------------------------ camera */
function mat3mul(a, b) {
  const o = new Array(9);
  for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++)
    o[r * 3 + c] = a[r * 3] * b[c] + a[r * 3 + 1] * b[3 + c] + a[r * 3 + 2] * b[6 + c];
  return o;
}

/** Model rotation: spin about the pole, stand the pole up, then tilt. */
function modelRot() {
  const cy = Math.cos(S.yaw), sy = Math.sin(S.yaw);
  const cp = Math.cos(S.pitch), sp = Math.sin(S.pitch);
  const Rz = [cy, -sy, 0, sy, cy, 0, 0, 0, 1];
  const Map = [1, 0, 0, 0, 0, 1, 0, -1, 0];
  const Rx = [1, 0, 0, 0, cp, -sp, 0, sp, cp];
  return mat3mul(Rx, mat3mul(Map, Rz));
}
/** Row-major 3x3 -> the column-major layout WebGL wants. */
function col3(m) {
  return new Float32Array([m[0], m[3], m[6], m[1], m[4], m[7], m[2], m[5], m[8]]);
}

const FOV0 = 40 * DEG;
const fovNow = () => {
  const base = Math.min(FOV0 / Math.min(1, S.aspect || 1), 78 * DEG);
  return 2 * Math.atan(Math.tan(base / 2) / S.zoom);
};

function viewProj(aspect) {
  S.aspect = aspect;
  const fov = fovNow();
  const f = 1 / Math.tan(fov / 2);
  const near = 0.05, far = 12;
  const nf = 1 / (near - far);
  const proj = new Float32Array([
    f / aspect, 0, 0, 0, 0, f, 0, 0, 0, 0, (far + near) * nf, -1, 0, 0, 2 * far * near * nf, 0]);
  const view = new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,-S.dist,1]);
  return M4.mul(proj, view);
}

/* ------------------------------------------------------------------ render */
let W = 0, H = 0, DPR = 1;
function resize() {
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  const w = cv.clientWidth, h = cv.clientHeight;
  if (!w || !h) return;
  W = Math.round(w * DPR); H = Math.round(h * DPR);
  if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
}

const SUN = (() => { const v = [-0.38, 0.34, 0.86]; const n = Math.hypot(...v); return v.map(x => x / n); })();

let now = 0;
function draw() {
  if (!S.ready) return;
  now = performance.now() / 1000;
  resize();
  gl.viewport(0, 0, W, H);
  gl.clear(gl.COLOR_BUFFER_BIT);

  const VP = viewProj(W / H);
  const R = col3(modelRot());
  const eye = [0, 0, 1];
  const ice = at(CH.curves.ice, S.t);
  const green = at(CH.curves.green, S.t);
  const hot = clamp((at(CH.curves.temp, S.t) - 12) / 18, 0, 1);
  const molten = at(CH.curves.molten, S.t);
  /* Past the end of the plate model there is no reconstruction to show, so the
     oldest one is held and dimmed rather than presented as fact. */
  const fade = (S.t > PL.ageMax ? 0.4 : 1) * (1 - molten);

  /* ocean */
  let p = P.sphere;
  gl.useProgram(p);
  gl.uniformMatrix4fv(p.u.uVP, false, VP);
  gl.uniformMatrix3fv(p.u.uRot, false, R);
  gl.uniform3fv(p.u.uEye, eye); gl.uniform3fv(p.u.uSun, SUN);
  gl.uniform1f(p.u.uDist, S.dist); gl.uniform1f(p.u.uIce, ice);
  gl.uniform1f(p.u.uSea, at(CH.curves.sea, S.t)); gl.uniform1f(p.u.uHot, hot);
  gl.uniform1f(p.u.uMolten, at(CH.curves.molten, S.t));
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.sphere);
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
  gl.disableVertexAttribArray(1);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buf.sphereIdx);
  gl.drawElements(gl.TRIANGLES, buf.sphereCount, gl.UNSIGNED_INT, 0);

  /* shelf, then land */
  p = P.land;
  gl.useProgram(p);
  gl.uniformMatrix4fv(p.u.uVP, false, VP);
  gl.uniformMatrix3fv(p.u.uRot, false, R);
  gl.uniform3fv(p.u.uEye, eye); gl.uniform3fv(p.u.uSun, SUN);
  gl.uniform1f(p.u.uDist, S.dist); gl.uniform1f(p.u.uIce, ice);
  gl.uniform1f(p.u.uTime, Math.min(S.t, PL.ageMax)); gl.uniform1f(p.u.uGreen, green);
  gl.uniform1i(p.u.uFeat, 0); gl.uniform1i(p.u.uQuat, 1);
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.pos);
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 3, gl.SHORT, true, 6, 0);
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.fid);
  gl.enableVertexAttribArray(1);
  gl.vertexAttribIPointer(1, 1, gl.UNSIGNED_SHORT, 2, 0);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buf.idx);
  gl.uniform1f(p.u.uFade, fade);
  if (fade > 0.04) {
    gl.uniform1f(p.u.uShelf, 1); gl.uniform1f(p.u.uLift, 1.0016);
    gl.drawElements(gl.TRIANGLES, PL.shelf.count, gl.UNSIGNED_SHORT, PL.shelf.first * 2);
    gl.uniform1f(p.u.uShelf, 0); gl.uniform1f(p.u.uLift, 1.0032);
    gl.drawElements(gl.TRIANGLES, PL.land.count, gl.UNSIGNED_SHORT, PL.land.first * 2);
  }
  gl.disableVertexAttribArray(1);

  /* latitude circles */
  p = P.grid;
  gl.useProgram(p);
  gl.uniformMatrix4fv(p.u.uVP, false, VP);
  gl.uniformMatrix3fv(p.u.uRot, false, R);
  gl.uniform3fv(p.u.uEye, eye); gl.uniform1f(p.u.uDist, S.dist);
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.grid);
  gl.enableVertexAttribArray(0);
  gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
  for (const r of buf.gridRuns) {
    gl.uniform4f(p.u.uCol, 1, 1, 1, r.major ? 0.20 : 0.09);
    gl.drawArrays(gl.LINE_STRIP, r.start, r.count);
  }

  /* the searched region */
  if (S.ring) {
    const pi = plateIndex.get(S.ring.plate);
    let c = S.ring.v;
    if (pi !== undefined) {
      c = qrot([quatData[pi * 4], quatData[pi * 4 + 1],
                quatData[pi * 4 + 2], quatData[pi * 4 + 3]], c);
    }
    const puls = 0.5 + 0.5 * Math.sin(now * 1.9);
    const rad = S.ring.rad * (1 + 0.035 * puls);
    buildRing(c, rad, Math.max(0.0055, rad * 0.075));
    p = P.ring;
    gl.useProgram(p);
    gl.uniformMatrix4fv(p.u.uVP, false, VP);
    gl.uniformMatrix3fv(p.u.uRot, false, R);
    gl.uniform3fv(p.u.uEye, eye);
    gl.uniform1f(p.u.uDist, S.dist);
    gl.uniform1f(p.u.uAlpha, 0.55 + 0.25 * puls);
    const col = S.ringCol || [1, 1, 1];
    gl.uniform3f(p.u.uCol, col[0], col[1], col[2]);
    gl.bindBuffer(gl.ARRAY_BUFFER, buf.ring);
    gl.bufferData(gl.ARRAY_BUFFER, ringXYZ, gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, buf.ringT);
    gl.enableVertexAttribArray(1);
    gl.vertexAttribPointer(1, 1, gl.FLOAT, false, 0, 0);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, (RING_SEG + 1) * 2);
    gl.disableVertexAttribArray(1);
  }

  /* fossil localities */
  if (pins && S.pins && fade > 0.9) {
    p = P.pin;
    gl.useProgram(p);
    gl.uniformMatrix4fv(p.u.uVP, false, VP);
    gl.uniformMatrix3fv(p.u.uRot, false, R);
    gl.uniform3fv(p.u.uEye, eye);
    gl.uniform1f(p.u.uDist, S.dist); gl.uniform1f(p.u.uTime, S.t);
    gl.uniform1f(p.u.uPx, DPR); gl.uniform1f(p.u.uSel, S.sel);
    gl.uniform1f(p.u.uFilter, S.filter ? 1 : 0);
    gl.uniform1f(p.u.uPulse, 0.5 + 0.5 * Math.sin(now * 3.1));
    gl.uniform1i(p.u.uQuat, 1);
    gl.uniform3fv(p.u.uGroupCol, new Float32Array(GROUP_COLOR.flat()));
    gl.uniform1fv(p.u.uGroupOn, new Float32Array(S.groupOn));
    gl.bindBuffer(gl.ARRAY_BUFFER, buf.pin);
    for (let i = 0; i < 6; i++) gl.enableVertexAttribArray(i);
    gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 32, 0);
    gl.vertexAttribPointer(1, 1, gl.FLOAT, false, 32, 12);
    gl.vertexAttribPointer(2, 1, gl.FLOAT, false, 32, 16);
    gl.vertexAttribPointer(3, 2, gl.FLOAT, false, 32, 20);
    gl.vertexAttribPointer(4, 1, gl.FLOAT, false, 32, 28);
    gl.bindBuffer(gl.ARRAY_BUFFER, buf.match);
    gl.vertexAttribPointer(5, 1, gl.FLOAT, false, 4, 0);
    gl.drawArrays(gl.POINTS, 0, pins.n);
    for (let i = 1; i < 6; i++) gl.disableVertexAttribArray(i);
  }

  updateLabels();
}

/* --------------------------------------------------------------- main loop */
let lastT = -1, lastFrame = 0;
function frame(ts) {
  requestAnimationFrame(frame);
  if (!S.ready) return;
  const dt = Math.min((ts - lastFrame) / 1000 || 0, 0.05);
  lastFrame = ts;

  if (S.fly) {
    S.fly.t = Math.min(1, S.fly.t + dt / 0.75);
    const u = S.fly.t < 0.5 ? 4 * S.fly.t ** 3 : 1 - Math.pow(-2 * S.fly.t + 2, 3) / 2;
    S.yaw = S.fly.y0 + (S.fly.y1 - S.fly.y0) * u;
    S.pitch = S.fly.p0 + (S.fly.p1 - S.fly.p0) * u;
    S.zoom = S.fly.z0 + (S.fly.z1 - S.fly.z0) * u;
    if (S.fly.t >= 1) S.fly = null;
  }
  if (S.spin) { S.yaw += dt * 0.12; }
  if (S.play) {
    const max = reader.scrollHeight - reader.clientHeight;
    const next = reader.scrollTop + dt * (max / 175);
    if (next >= max) { setPlay(false); reader.scrollTop = max; }
    else reader.scrollTop = next;
  }
  if (S.t !== lastT) { poseAt(Math.min(S.t, PL.ageMax)); lastT = S.t; }
  draw();
}

/* --------------------------------------------------------------- projection
   Same transform as the vertex shader, on the CPU, so a click can be matched
   to a locality. */
function screenOf(i) {
  const a = pins.data, k = i * 8;
  const pi = a[k + 3];
  const q = [quatData[pi * 4], quatData[pi * 4 + 1], quatData[pi * 4 + 2], quatData[pi * 4 + 3]];
  const v = qrot(q, [a[k], a[k + 1], a[k + 2]]);
  const m = modelRot();
  const w = [
    m[0] * v[0] + m[1] * v[1] + m[2] * v[2],
    m[3] * v[0] + m[4] * v[1] + m[5] * v[2],
    m[6] * v[0] + m[7] * v[1] + m[8] * v[2]];
  const len = Math.hypot(...w);
  if (w[2] / len <= 1 / S.dist + 0.004) return null;      /* over the horizon */
  const f = 1 / Math.tan(fovNow() / 2);
  const aspect = cv.clientWidth / cv.clientHeight;
  const vz = w[2] * 1.004 - S.dist;
  if (vz >= -0.01) return null;
  const ndcx = (f / aspect) * w[0] * 1.004 / -vz;
  const ndcy = f * w[1] * 1.004 / -vz;
  return [(ndcx * 0.5 + 0.5) * cv.clientWidth, (0.5 - ndcy * 0.5) * cv.clientHeight];
}

function pick(px, py) {
  if (!pins || !S.pins) return -1;
  const d = chData[pins.chapter];
  if (!d) return -1;
  let best = -1, bd = 18 * 18;
  for (let i = 0; i < pins.n; i++) {
    const src = pins.map[i];
    if (!S.groupOn[Math.min(d.sites.g[src], 12)]) continue;
    if (S.t > d.sites.ea[src] + 0.001 || S.t < d.sites.la[src] - 0.001) continue;
    const s = screenOf(i);
    if (!s) continue;
    const dx = s[0] - px, dy = s[1] - py, dd = dx * dx + dy * dy;
    if (dd < bd) { bd = dd; best = i; }
  }
  return best;
}

/* ------------------------------------------------------------------ reader */
const el = (tag, cls, text) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
};
/* Chapter prose marks scientific names with *asterisks*. */
function prose(text) {
  const p = el('p');
  text.split(/(\*[^*]+\*)/).forEach(part => {
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2)
      p.appendChild(el('em', null, part.slice(1, -1)));
    else if (part) p.appendChild(document.createTextNode(part));
  });
  return p;
}
const ageText = a => a >= 1000 ? (a / 1000).toFixed(a >= 100 ? 2 : 3) + ' Ga'
  : a >= 1 ? Math.round(a) + ' Ma'
  : a >= 0.001 ? Math.round(a * 1000) + ' ka'
  : 'today';

/** An image plus its provenance, both linking to the file page it came from. */
function photo(key, alt) {
  const rec = IMG[key];
  if (!rec || !rec.u) return null;
  const img = el('img');
  img.loading = 'lazy'; img.decoding = 'async';
  img.alt = alt || '';
  img.src = rec.u;

  let node = img;
  if (rec.p) {
    const a = el('a', 'shot');
    a.href = rec.p;
    a.target = '_blank';
    a.rel = 'noopener';
    a.title = 'View this photograph on Wikimedia' + (rec.a ? ' \u2014 by ' + rec.a : '');
    a.appendChild(img);
    node = a;
  }
  return { node, img, credit: [rec.a, rec.l].filter(Boolean).join(' \u00b7 '),
           page: rec.p || '' };
}

/** Credit line, linked to the source when we know where it lives. */
function creditLine(p, cls) {
  if (!p.credit && !p.page) return null;
  const text = p.credit || 'Source';
  if (!p.page) return el('span', cls, text);
  const a = el('a', cls + ' src', text);
  a.href = p.page;
  a.target = '_blank';
  a.rel = 'noopener';
  a.title = 'Open the source file page';
  return a;
}

const sections = [];
const reader = $('reader');

function buildReader() {
  const host = $('chapters');
  CH.chapters.forEach((c, i) => {
    const sec = el('section', 'chapter');
    sec.id = 'ch-' + c.id;
    sec.style.setProperty('--accent', c.color);
    sec.style.setProperty('--accent-soft', c.color + '22');
    const w = el('div', 'wrap');
    sec.appendChild(w);

    const no = el('div', 'no');
    no.appendChild(el('i'));
    no.appendChild(el('span', null, `${c.eon} · ${c.era}`));
    w.appendChild(no);
    w.appendChild(el('h2', null, c.name));
    w.appendChild(el('div', 'sub', c.sub));
    const span = c.end === 0 ? `${ageText(c.start)} — today`
      : `${ageText(c.start)} — ${ageText(c.end)}`;
    const dur = c.start - c.end;
    w.appendChild(el('div', 'span',
      `${span}  ·  ${dur >= 1 ? Math.round(dur).toLocaleString() + ' million years long'
        : Math.round(dur * 1000).toLocaleString() + ' thousand years long'}`));
    w.appendChild(el('div', 'lede2', c.lede));

    const world = el('div', 'world');
    world.appendChild(el('p', null, c.world));
    const row = el('div', 'row');
    world.appendChild(row);
    w.appendChild(world);
    sec.dataset.climate = '1';

    const pr = el('div', 'prose');
    c.story.forEach(t => pr.appendChild(prose(t)));
    w.appendChild(pr);

    /* scene photographs */
    const shots = c.scenes.map(t => ({ t, p: photo('sc:' + t, t) })).filter(x => x.p);
    if (shots.length) {
      w.appendChild(el('h3', 'sec', 'The world then'));
      const g = el('div', 'gal');
      shots.slice(0, 4).forEach((x, k) => {
        const fig = el('figure', k === 0 && shots.length % 2 ? 'wide' : '');
        fig.appendChild(x.p.node);
        const cap = el('figcaption', null, IMG['sc:' + x.t].c || x.t);
        const cr = creditLine(x.p, 'cr');
        if (cr) cap.appendChild(cr);
        fig.appendChild(cap);
        g.appendChild(fig);
      });
      w.appendChild(g);
    }

    if (c.events.length) {
      w.appendChild(el('h3', 'sec', 'What happened'));
      const ul = el('ul', 'events');
      c.events.forEach(ev => {
        const li = el('li');
        const a = el('div', 'age', ageText(ev.age));
        a.title = 'Go to this moment';
        a.onclick = () => goToAge(ev.age);
        li.appendChild(a);
        const d = el('div');
        d.appendChild(el('b', null, ev.title));
        d.appendChild(el('p', null, ev.text));
        li.appendChild(d);
        ul.appendChild(li);
      });
      w.appendChild(ul);
    }

    if (c.firsts.length) {
      w.appendChild(el('h3', 'sec', 'First seen in this chapter'));
      const ch = el('div', 'chips');
      c.firsts.forEach(f => ch.appendChild(el('span', null, f)));
      w.appendChild(ch);
    }

    if (c.featured.length) {
      w.appendChild(el('h3', 'sec', 'Life of the ' + c.name));
      const grid = el('div', 'life');
      c.featured.forEach(f => {
        const card = el('div', 'card');
        const p = photo('sp:' + f.name, f.name);
        if (p) card.appendChild(p.node);
        const t = el('div', 't');
        t.appendChild(el('b', null, f.name));
        t.appendChild(el('p', null, f.note));
        const cr = p && creditLine(p, 'cr');
        if (cr) t.appendChild(cr);
        card.appendChild(t);
        grid.appendChild(card);
      });
      w.appendChild(grid);
    }

    w.appendChild(el('h3', 'sec', 'In the fossil record'));
    const fossil = el('div');
    fossil.id = 'fx-' + c.id;
    fossil.appendChild(el('div', 'nofossil', 'Loading the database…'));
    w.appendChild(fossil);

    host.appendChild(sec);
    sections.push({ el: sec, ch: c, i, climate: row });
  });

  /* sources */
  CH.sources.forEach(s => {
    const d = el('div');
    d.appendChild(el('b', null, s.what));
    d.appendChild(document.createTextNode(s.cite));
    $('sources').appendChild(d);
  });
  $('disclaimer').textContent = CH.disclaimer;

  /* true-scale bar in the hero: how little of it we are used to thinking about */
  const total = CH.chapters[0].start;
  CH.chapters.forEach(c => {
    const d = el('div');
    d.style.cssText = `flex:${(c.start - c.end) / total} 0 0;background:${c.color}`;
    d.title = `${c.name} — ${ageText(c.start)} to ${ageText(c.end)}`;
    $('scaletrack').appendChild(d);
  });
  const cam = CH.chapters.find(c => c.id === 'cambrian');
  if (cam) {
    const m = el('div', 'mark');
    m.style.left = ((total - cam.start) / total * 100) + '%';
    m.appendChild(el('b', null, 'Cambrian'));
    $('scalebar').appendChild(m);
  }
}

/** Fill a chapter's fossil panel once its data file has arrived. */
function renderFossils(c, d) {
  const host = $('fx-' + c.id);
  if (!host) return;
  host.textContent = '';
  if (!d) {
    host.appendChild(el('div', 'nofossil',
      'Nothing from this chapter is catalogued in the Paleobiology Database — '
      + 'the fossils of this age are microscopic, chemical, or simply not there.'));
    return;
  }
  const n = d.counts;
  const row = el('div', 'world');
  const line = el('p');
  line.innerHTML = `The Paleobiology Database holds <b>${n.occs.toLocaleString()}</b> `
    + `fossil occurrences from this chapter, covering <b>${n.genera.toLocaleString()}</b> `
    + `genera at <b>${n.colls.toLocaleString()}</b> localities. `
    + `<b>${n.sites.toLocaleString()}</b> of those localities are on the globe — `
    + `click one to see what came out of it.`;
    line.style.fontFamily = 'var(--prose)';
  row.appendChild(line);
  host.appendChild(row);

  const top = d.breakdown.slice(0, 8);
  const max = Math.max(...top.map(b => b.genera));
  const bars = el('div', 'bars');
  bars.style.marginTop = '18px';
  top.forEach(b => {
    const r = el('div', 'bar');
    r.appendChild(el('div', 'nm', d.groups[b.g]));
    const tr = el('div', 'tr');
    const fill = el('i');
    fill.style.cssText = `width:${(b.genera / max * 100).toFixed(1)}%;background:${css(GROUP_COLOR[Math.min(b.g, 12)])}`;
    tr.appendChild(fill);
    r.appendChild(tr);
    r.appendChild(el('div', 'vv', b.genera.toLocaleString()));
    bars.appendChild(r);
  });
  host.appendChild(bars);

  if (d.roster.length) {
    const rr = el('div', 'roster');
    const list = el('div', 'list');
    d.roster.forEach(g => list.appendChild(el('i', null, g[0])));
    rr.appendChild(list);
    const btn = el('button', 'more',
      `Show all ${d.roster.length} of the commonest genera`);
    btn.onclick = () => {
      list.classList.toggle('open');
      btn.textContent = list.classList.contains('open')
        ? 'Collapse the list' : `Show all ${d.roster.length} of the commonest genera`;
    };
    rr.appendChild(btn);
    host.appendChild(rr);
  }
}

/* -------------------------------------------------------------- data loads */
const pending = {};
function loadChapter(i) {
  const c = CH.chapters[i];
  if (!c || c.id in chData || c.id in pending) return;
  if (chIndex && !(c.id in chIndex)) {   /* older than the fossil record */
    chData[c.id] = null;
    renderFossils(c, null);
    return;
  }
  pending[c.id] = 1;
  fetch(url('ch/' + c.id + '.json'))
    .then(r => r.ok ? r.json() : null)
    .catch(() => null)
    .then(d => {
      chData[c.id] = d;
      renderFossils(c, d);
      if (S.ch === i) { uploadPins(d); syncLegend(); reapplyFilter(); }
    });
}

/* -------------------------------------------------- scroll drives the clock */
let docH = -1;
let totalH = 1;
function layout() {
  const sy = reader.scrollTop;
  const base = reader.getBoundingClientRect().top;
  sections.forEach(s => {
    const r = s.el.getBoundingClientRect();
    s.top = r.top - base + sy;
    s.h = r.height;
  });
  const total = totalH = sections.reduce((a, s) => a + s.h, 0) || 1;
  const railW = $('track').clientWidth || 600;
  $('segs').textContent = '';
  sections.forEach(s => {
    const d = el('div');
    d.style.cssText = `flex:${s.h / total} 0 0;background:${s.ch.color}`;
    d.title = s.ch.name;
    if (s.h / total * railW > 58) d.appendChild(el('span', null, s.ch.name));
    d.onclick = e => { e.stopPropagation(); goToChapter(s.i); };
    $('segs').appendChild(d);
  });
  docH = reader.scrollHeight;
}

/** Where the reader's eye is, as a (chapter, progress) pair. */
function readPosition() {
  const y = reader.scrollTop + reader.clientHeight * 0.42;
  if (!sections.length) return null;
  if (y < sections[0].top) return { i: 0, p: 0, before: true };
  for (let i = sections.length - 1; i >= 0; i--) {
    const s = sections[i];
    if (y >= s.top) return { i, p: clamp((y - s.top) / (s.h || 1), 0, 1) };
  }
  return { i: 0, p: 0 };
}

let accentNow = '';
function onScroll() {
  if (reader.scrollHeight !== docH) layout();
  const pos = readPosition();
  if (!pos) return;
  const c = CH.chapters[pos.i];
  S.prog = pos.p;
  S.t = pos.before ? CH.chapters[0].start : c.start + (c.end - c.start) * pos.p;

  if (pos.i !== S.ch) {
    S.ch = pos.i;
    S.sel = -1; $('site').classList.remove('on');
    const d = chData[c.id];
    if (d !== undefined) { uploadPins(d); syncLegend(); reapplyFilter(); }
    else { pins = null; loadChapter(pos.i); }
    if (qbox.value.trim().length >= 2 && document.activeElement === qbox)
      renderResults(search(qbox.value), qbox.value);
    loadChapter(pos.i + 1); loadChapter(pos.i - 1);
  }
  if (accentNow !== c.color) {
    accentNow = c.color;
    document.documentElement.style.setProperty('--accent', c.color);
    document.documentElement.style.setProperty('--accent-soft', c.color + '22');
    $('chip').textContent = c.name;
    $('railname').textContent = c.name;
  }
  updateHUD();

  let acc = 0;
  for (let i = 0; i < pos.i; i++) acc += sections[i].h;
  $('head').style.left =
    ((acc + pos.p * (sections[pos.i] ? sections[pos.i].h : 0)) / totalH * 100) + '%';
}

function goToChapter(i, p = 0.02) {
  const s = sections[i];
  if (!s) return;
  setPlay(false);
  reader.scrollTo({ top: s.top + s.h * p - reader.clientHeight * 0.42, behavior: 'smooth' });
}
function goToAge(age) {
  for (let i = 0; i < CH.chapters.length; i++) {
    const c = CH.chapters[i];
    if (age <= c.start && age >= c.end) {
      const p = c.start === c.end ? 0 : (c.start - age) / (c.start - c.end);
      return goToChapter(i, clamp(p, 0.01, 0.99));
    }
  }
}

/* ------------------------------------------------------------------- HUD */
/* One table drives both the readout tiles and the panel that explains them, so
   a number can never end up on screen without a definition behind it. */
const METRICS = [
  { label: 'Global temp', unit: '',
    value: c => c.temp.toFixed(0) + '°C',
    what: 'Mean surface temperature averaged over the whole planet and the whole '
        + 'year. Today it is about 15°C, so the number is directly comparable to '
        + 'the figure you see in climate reporting.',
    src: 'Temperature' },
  { label: 'CO₂', unit: 'ppm',
    value: c => Math.round(c.co2).toLocaleString(),
    what: 'Carbon dioxide in the atmosphere, in parts per million by volume — the '
        + 'same unit throughout, from 250 ppm in the Carboniferous to 400,000 in '
        + 'the Hadean, when CO₂ was a large fraction of a very different air. '
        + 'Today: about 420 ppm.',
    src: 'CO₂' },
  { label: 'Oxygen', unit: '% of air',
    value: c => c.o2 < 1 ? '<1%' : c.o2.toFixed(0) + '%',
    what: 'Free O₂ as a percentage of the atmosphere. Effectively zero before the '
        + 'Great Oxidation Event, a peak near 35% in the Carboniferous coal '
        + 'forests, and 21% today.',
    src: 'O₂' },
  { label: 'Sea level', unit: 'vs today',
    value: c => c.t > 1000 ? '—' : (c.sea >= 0 ? '+' : '') + c.sea.toFixed(0) + 'm',
    what: 'Height of the global ocean surface measured against today’s sea level, '
        + 'which is the zero point. +200 m means the sea stood 200 metres higher '
        + 'than now and flooded the interiors of the continents; −120 m is a '
        + 'glacial maximum with that much water locked up in ice. Shown as “—” '
        + 'before 1,000 Ma, where there is no usable estimate.',
    src: 'Sea level' },
  { label: 'Polar ice', unit: 'reaches',
    value: c => c.ice >= 89 ? 'none' : 'to ' + c.ice.toFixed(0) + '°',
    what: 'The latitude that year-round ice reaches down to. “to 66°” means '
        + 'permanent ice from 66° to the pole — roughly today. “to 7°” is a '
        + 'Snowball Earth with ice almost at the equator, and “none” means no '
        + 'permanent polar ice at all, as through most of the Cretaceous. It is '
        + 'one symmetric number standing in for two hemispheres that are rarely '
        + 'symmetric, so read it as an index of how glaciated the world is, not '
        + 'as a measured ice margin.',
    src: 'Ice line' },
  { label: 'Plant cover', unit: 'of land',
    value: c => (c.green * 100).toFixed(0) + '%',
    what: 'Roughly how much of the land surface carries plants. Zero before the '
        + 'Ordovician, when the continents were bare rock; it climbs through the '
        + 'Devonian as forests appear, collapses at the end-Permian extinction, '
        + 'and recovers. This one also drives the colour of the land on the globe.',
    src: 'Land plant cover' },
];

let statBoxes = null;
function makeStats() {
  statBoxes = METRICS.map(m => {
    const box = el('div', 'stat');
    const v = el('b');
    box.appendChild(v);
    const lab = el('span', null, m.label);
    if (m.unit) lab.appendChild(el('i', null, m.unit));
    box.appendChild(lab);
    box.title = m.what.replace(/\s+/g, ' ');
    $('stats').appendChild(box);
    return { box, v };
  });
  const q = el('button');
  q.id = 'qmark';
  q.textContent = '?';
  q.title = 'What do these mean?';
  q.setAttribute('aria-label', 'What do these readouts mean?');
  q.onclick = () => toggleAbout();
  $('stats').appendChild(q);
}

function buildAbout() {
  const body = $('abody');
  const cite = Object.fromEntries(CH.sources.map(s => [s.what, s.cite]));
  METRICS.forEach(m => {
    const d = el('div', 'metric');
    const b = el('b', null, m.label);
    if (m.unit) b.appendChild(el('em', null, m.unit));
    d.appendChild(b);
    d.appendChild(el('p', null, m.what));
    if (cite[m.src]) d.appendChild(el('cite', null, cite[m.src]));
    body.appendChild(d);
  });
  const note = el('div', 'metric');
  note.appendChild(el('p', null, CH.disclaimer));
  body.appendChild(note);
}

function toggleAbout(force) {
  const on = force !== undefined ? force : !$('about').classList.contains('on');
  $('about').classList.toggle('on', on);
  const q = $('qmark');
  if (q) q.classList.toggle('on', on);
  if (on) hideSite();
}

function updateHUD() {
  const t = S.t;
  $('age').innerHTML = t < 0.002
    ? 'Today'
    : (t >= 1000
        ? (t / 1000).toFixed(2) + '<small>billion years ago</small>'
        : (t >= 1 ? Math.round(t).toLocaleString() : (t * 1000).toFixed(0) + ' thousand')
          + (t >= 1 ? '<small>million years ago</small>' : '<small>years ago</small>'));

  const c = {
    t,
    temp: at(CH.curves.temp, t), co2: at(CH.curves.co2, t),
    o2: at(CH.curves.o2, t), sea: at(CH.curves.sea, t),
    ice: at(CH.curves.ice, t), green: at(CH.curves.green, t),
  };
  if (!statBoxes) makeStats();
  METRICS.forEach((m, i) => {
    const v = m.value(c), b = statBoxes[i];
    if (b.v.textContent !== v) b.v.textContent = v;
  });
  $('stale').classList.toggle('on', t > PL.ageMax && at(CH.curves.molten, t) < 0.6);
}

/* ------------------------------------------------------------------ search
   Three things are searchable: places (every country and state the database
   has localities in, available at any age), and — within the chapter you are
   reading — the localities themselves and the fossils found in them. */
let PLACES = [];
const indexes = {};       /* chapter id -> searchable entries */

function chapterIndex(id) {
  if (indexes[id]) return indexes[id];
  const d = chData[id];
  const out = [];
  if (d) {
    const s = d.sites, n = s.lon.length;
    for (let i = 0; i < n; i++) {
      if (s.nm[i]) out.push({ k: 'locality', n: s.nm[i], site: i, w: s.n[i] });
    }
    const forms = new Map();
    for (let i = 0; i < n; i++) {
      const f = s.fm[i];
      if (!f) continue;
      const e = forms.get(f) || { k: 'formation', n: f, sites: [], w: 0 };
      e.sites.push(i); e.w += s.n[i];
      forms.set(f, e);
    }
    for (const e of forms.values()) out.push(e);

    /* every taxon name recorded at a locality, plus the chapter roster */
    const taxa = new Map();
    for (let i = 0; i < n; i++) {
      for (const j of s.tx[i]) {
        const nm = d.names[j];
        let e = taxa.get(nm);
        if (!e) taxa.set(nm, e = { k: 'fossil', n: nm, sites: [], w: 0 });
        e.sites.push(i); e.w += 1;
      }
    }
    for (const r of d.roster) {
      if (!taxa.has(r[0])) taxa.set(r[0], { k: 'fossil', n: r[0], sites: [], w: 0, occ: r[1] });
      else taxa.get(r[0]).occ = r[1];
    }
    for (const e of taxa.values()) out.push(e);
  }
  indexes[id] = out;
  return out;
}

function score(name, q) {
  const l = name.toLowerCase();
  const i = l.indexOf(q);
  if (i < 0) return -1;
  if (i === 0) return 3;                                   /* starts with it   */
  if (/[\s,(\-]/.test(l[i - 1])) return 2;                 /* starts a word    */
  return 1;
}

function search(q) {
  q = q.trim().toLowerCase();
  if (q.length < 2) return [];
  const hits = [];
  const push = (e, base, weight) => {
    const sc = score(e.n, q);
    if (sc > 0) hits.push({ e, rank: sc * 1000 + base + Math.min(weight || 0, 900) });
  };
  for (const p of PLACES) push(p, 300, Math.log10(1 + p.c) * 120);
  const idx = chapterIndex(CH.chapters[S.ch].id);
  for (const e of idx) {
    push(e, e.k === 'fossil' ? 200 : e.k === 'formation' ? 150 : 100,
         e.k === 'fossil' ? Math.log10(1 + (e.occ || e.w)) * 120 : (e.w || 0) * 2);
  }
  hits.sort((a, b) => b.rank - a.rank);
  const seen = new Set(), out = [];
  for (const h of hits) {
    const key = h.e.k + '|' + h.e.n;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(h.e);
    if (out.length >= 12) break;
  }
  return out;
}

function mark(name, q) {
  const span = el('span', 'nm');
  const i = name.toLowerCase().indexOf(q.trim().toLowerCase());
  if (i < 0 || !q.trim()) { span.textContent = name; return span; }
  const n = q.trim().length;
  span.appendChild(document.createTextNode(name.slice(0, i)));
  span.appendChild(el('b', null, name.slice(i, i + n)));
  span.appendChild(document.createTextNode(name.slice(i + n)));
  return span;
}

let results = [], resultSel = -1;
function renderResults(list, q) {
  const box = $('qres');
  box.textContent = '';
  results = list; resultSel = -1;
  if (!q.trim() || q.trim().length < 2) { box.classList.remove('on'); return; }
  if (!list.length) {
    const d = el('div', 'qempty');
    d.textContent = 'Nothing here by that name. Places work in any chapter; '
      + 'fossils and localities are searched within the ' + CH.chapters[S.ch].name + '.';
    box.appendChild(d);
    box.classList.add('on');
    return;
  }
  list.forEach((e, i) => {
    const row = el('div', 'qr');
    row.setAttribute('role', 'option');
    row.appendChild(el('span', 'kind', e.k === 'country' || e.k === 'region' ? 'place' : e.k));
    row.appendChild(mark(e.n, q));
    let sub = '';
    if (e.k === 'country' || e.k === 'region') {
      sub = e.c.toLocaleString() + ' sites';
      row.title = `${e.n} — ${e.c.toLocaleString()} localities across all of time; `
        + 'the globe will turn to it at whatever age you are on';
    }
    else if (e.k === 'fossil') sub = e.sites.length ? e.sites.length + ' here' : 'in the record';
    else if (e.k === 'formation') sub = e.sites.length + ' sites';
    else if (e.k === 'locality') sub = e.w + ' taxa';
    if (sub) row.appendChild(el('span', 'sub', sub));
    row.onmousedown = ev => { ev.preventDefault(); choose(i); };
    box.appendChild(row);
  });
  box.classList.add('on');
}

function highlightResult(d) {
  const rows = [...$('qres').children];
  if (!rows.length) return;
  resultSel = (resultSel + d + rows.length) % rows.length;
  rows.forEach((r, i) => r.classList.toggle('sel', i === resultSel));
  rows[resultSel].scrollIntoView({ block: 'nearest' });
}

/* ---- marking the answer on the globe */
const DEFAULT_RING = { country: 7, region: 4.2 };

/** Circle that covers a place's localities in the chapter being read. */
function ringFor(place, siteIdx) {
  const v = unitAt(place.lon, place.lat);
  let rad = DEFAULT_RING[place.k] || 5;
  const d = chData[CH.chapters[S.ch].id];
  if (d && siteIdx && siteIdx.length) {
    const gaps = [];
    for (const i of siteIdx) {
      const w = unitAt(d.sites.lon[i], d.sites.lat[i]);
      gaps.push(Math.acos(clamp(v[0] * w[0] + v[1] * w[1] + v[2] * w[2], -1, 1)) / DEG);
    }
    gaps.sort((a, b) => a - b);
    rad = gaps[Math.floor(gaps.length * 0.92)] + 1.6;
  }
  return { v, plate: place.p, rad: clamp(rad, 2.4, 24) * DEG };
}

const labelPool = [];
function labelEl(i) {
  while (labelPool.length <= i) {
    const e = el('div', 'plab');
    $('labels').appendChild(e);
    labelPool.push(e);
  }
  return labelPool[i];
}

/** Position the search labels; called every frame, so it stays glued while the
    globe turns. */
function updateLabels() {
  const want = S.labels || [];
  let used = 0;
  const placed = [];
  const st = cv.getBoundingClientRect();
  const hud = $('hud').getBoundingClientRect();
  const floor = hud.bottom - st.top + 10;      /* keep clear of the readout */
  for (const lab of want) {
    let pt = null;
    if (lab.pin >= 0 && pins && lab.pin < pins.n) pt = screenOf(lab.pin);
    else if (lab.v) pt = screenOfPoint(lab.v, lab.plate);
    if (!pt) continue;
    if (pt[1] < floor || pt[1] > st.height - 8) continue;
    let clash = false;
    for (const q of placed) {
      if (Math.abs(q[0] - pt[0]) < 132 && Math.abs(q[1] - pt[1]) < 26) { clash = true; break; }
    }
    if (clash) continue;
    placed.push(pt);
    const e = labelEl(used++);
    e.textContent = lab.text;
    e.className = 'plab on' + (lab.big ? ' big' : '');
    e.style.left = pt[0] + 'px';
    e.style.top = (pt[1] - (lab.big ? 0 : 15)) + 'px';
  }
  for (let i = used; i < labelPool.length; i++) labelPool[i].className = 'plab';
}

/** Same projection as screenOf, for a point given directly rather than by pin. */
function screenOfPoint(v0, plate) {
  const pi = plateIndex.get(plate);
  let v = v0;
  if (pi !== undefined) {
    v = qrot([quatData[pi * 4], quatData[pi * 4 + 1],
              quatData[pi * 4 + 2], quatData[pi * 4 + 3]], v0);
  }
  const m = modelRot();
  const w = [m[0] * v[0] + m[1] * v[1] + m[2] * v[2],
             m[3] * v[0] + m[4] * v[1] + m[5] * v[2],
             m[6] * v[0] + m[7] * v[1] + m[8] * v[2]];
  if (w[2] <= 1 / S.dist + 0.004) return null;
  const f = 1 / Math.tan(fovNow() / 2);
  const aspect = cv.clientWidth / cv.clientHeight;
  const vz = w[2] * 1.004 - S.dist;
  if (vz >= -0.01) return null;
  return [((f / aspect) * w[0] * 1.004 / -vz * 0.5 + 0.5) * cv.clientWidth,
          (0.5 - f * w[1] * 1.004 / -vz * 0.5) * cv.clientHeight];
}

/* ---- acting on a result */

/** Move the reader straight to an age, without the smooth scroll, so the globe
    can be aimed immediately afterwards. */
function jumpToAge(age) {
  for (let i = 0; i < CH.chapters.length; i++) {
    const c = CH.chapters[i];
    if (age <= c.start && age >= c.end) {
      const sec = sections[i];
      if (!sec) return;
      const p = c.start === c.end ? 0 : (c.start - age) / (c.start - c.end);
      reader.scrollTop = sec.top + sec.h * clamp(p, 0.005, 0.995)
        - reader.clientHeight * 0.42;
      onScroll();                      /* keep S.t and the markers in step */
      return;
    }
  }
}

/** A locality only exists between its own two ages.  If the reader is parked
    outside that window the markers are hidden, which makes a search look like
    it found nothing — so move time to where the answer actually is. */
function alignAge(siteIdx) {
  const d = chData[CH.chapters[S.ch].id];
  if (!d || !siteIdx || !siteIdx.length) return false;
  const ea = d.sites.ea, la = d.sites.la;
  if (siteIdx.some(i => S.t <= ea[i] + 1e-6 && S.t >= la[i] - 1e-6)) return false;

  let bestT = null, bestN = -1, bestGap = Infinity;
  for (const i of siteIdx) {
    const mid = (ea[i] + la[i]) / 2;
    let n = 0;
    for (const j of siteIdx) if (mid <= ea[j] + 1e-6 && mid >= la[j] - 1e-6) n++;
    const gap = Math.abs(mid - S.t);
    if (n > bestN || (n === bestN && gap < bestGap)) { bestN = n; bestGap = gap; bestT = mid; }
  }
  if (bestT == null) return false;
  jumpToAge(bestT);
  return true;
}
function unitAt(lon, lat) {
  const la = lat * DEG, lo = lon * DEG, c = Math.cos(la);
  return [c * Math.cos(lo), c * Math.sin(lo), Math.sin(la)];
}

/** Half-angle of the globe's surface actually visible at a given zoom.  A ray
    α off the view axis meets the sphere θ from the sub-camera point, with
    sin(θ+α) = dist·sin α. */
function visibleHalfAngle(zoom) {
  const base = Math.min(FOV0 / Math.min(1, S.aspect || 1), 78 * DEG);
  const av = Math.atan(Math.tan(base / 2) / zoom);
  const ah = Math.atan(Math.tan(av) * (S.aspect || 1));
  const a = Math.min(av, ah);
  const s0 = S.dist * Math.sin(a);
  if (s0 >= 1) return Math.acos(1 / S.dist);
  return Math.asin(s0) - a;
}

/** Largest zoom that still shows a cap of angular radius `rad`, with margin. */
function zoomForRadius(rad) {
  const want = Math.min(rad * 1.45, Math.acos(1 / S.dist) * 0.95);
  let lo = 1, hi = 7;
  for (let i = 0; i < 22; i++) {
    const z = (lo + hi) / 2;
    if (visibleHalfAngle(z) >= want) lo = z; else hi = z;
  }
  return clamp(lo, 1, 7);
}

/** How far below centre to aim, so the target does not land behind the readout.
    Zero on a tall stage, where the middle is already clear. */
function aimBias(zoom) {
  const st = cv.getBoundingClientRect();
  const hud = $('hud').getBoundingClientRect();
  if (!st.height) return 0;
  const centre = st.height / 2;
  const desired = Math.min(hud.bottom - st.top + 34, st.height * 0.72);
  if (desired <= centre + 6) return 0;
  const k = (desired - centre) / centre;          /* in NDC half-heights */
  const base = Math.min(FOV0 / Math.min(1, S.aspect || 1), 78 * DEG);
  const f = 1 / Math.tan(2 * Math.atan(Math.tan(base / 2) / zoom) / 2);
  return Math.asin(clamp(k * (S.dist - 1) / f, -0.85, 0.85));
}

/** Turn the globe so a point on some plate faces the camera at the current age. */
function flyTo(lon, lat, plate, zoom) {
  const pi = plateIndex.get(plate);
  let v = unitAt(lon, lat);
  if (pi !== undefined) {
    v = qrot([quatData[pi * 4], quatData[pi * 4 + 1], quatData[pi * 4 + 2], quatData[pi * 4 + 3]], v);
  }
  /* modelRot = Rx(pitch) . Map . Rz(yaw); solving it to put v at the centre
     has two branches, and this is the one that keeps |pitch| under 90 degrees
     so the globe never ends up upside down. */
  const r2 = Math.hypot(v[0], v[1]);
  const yaw = Math.atan2(v[0], v[1]) + Math.PI;
  const z = zoom === undefined ? S.zoom : zoom;
  const pitch = clamp(Math.atan2(v[2], r2) + aimBias(z), -1.45, 1.45);
  /* take the short way round rather than unwinding the long way */
  let dy = yaw - S.yaw;
  while (dy > Math.PI) dy -= 2 * Math.PI;
  while (dy < -Math.PI) dy += 2 * Math.PI;
  S.fly = { y0: S.yaw, y1: S.yaw + dy, p0: S.pitch, p1: pitch,
            z0: S.zoom, z1: zoom === undefined ? S.zoom : zoom, t: 0 };
  S.spin = false; $('spin').classList.remove('on');
}

function setFilter(label, siteIdx, kind, emptyMsg) {
  if (!pins) return;
  if (!siteIdx) {
    S.filter = S.filterKind = null;
    S.ring = null; S.labels = null;
    if (pins.match) { pins.match.fill(0); uploadMatch(); }
    $('filter').classList.remove('on');
    return;
  }
  const want = new Set(siteIdx);
  let n = 0;
  for (let i = 0; i < pins.n; i++) {
    const on = want.has(pins.map[i]) ? 1 : 0;
    pins.match[i] = on;
    n += on;
  }
  uploadMatch();
  S.filter = label;
  if (kind) S.filterKind = kind;
  S.labels = labelsFor(siteIdx, kind, label);
  $('fmsg').textContent = n
    ? `${n.toLocaleString()} ${n === 1 ? 'locality' : 'localities'} · ${label}`
    : (emptyMsg || `${label} — none in the ${CH.chapters[S.ch].name}`);
  $('filter').classList.add('on');
}

/** Up to a dozen names, richest first, so a search reads on the globe itself. */
function labelsFor(siteIdx, kind, label) {
  const d = chData[CH.chapters[S.ch].id];
  const out = [];
  if ((kind === 'country' || kind === 'region') && S.ring) {
    out.push({ v: S.ring.v, plate: S.ring.plate, text: label, big: true });
  }
  if (!d || !pins || !siteIdx.length) return out;
  const ranked = siteIdx.slice().sort((a, b) => d.sites.n[b] - d.sites.n[a]).slice(0, 8);
  for (const i of ranked) {
    const packed = pins.map.indexOf(i);
    if (packed < 0) continue;
    let name = d.sites.nm[i] || (d.locs && d.sites.lc[i] >= 0 ? d.locs[d.sites.lc[i]] : '');
    if (!name) continue;
    if (name.length > 34) name = name.slice(0, 33).trimEnd() + '…';
    out.push({ pin: packed, text: name });
  }
  return out;
}

function uploadMatch() {
  gl.bindBuffer(gl.ARRAY_BUFFER, buf.match);
  gl.bufferSubData(gl.ARRAY_BUFFER, 0, pins.match);
}

/** Sites in the current chapter that sit in a named country or state. */
function sitesInPlace(name) {
  const d = chData[CH.chapters[S.ch].id];
  if (!d || !d.locs) return [];
  const hit = new Set();
  d.locs.forEach((label, i) => {
    if (label === name || label.endsWith(', ' + name)) hit.add(i);
  });
  const out = [];
  const lc = d.sites.lc || [];
  for (let i = 0; i < lc.length; i++) if (hit.has(lc[i])) out.push(i);
  return out;
}

function reapplyFilter() {
  const f = S.filter && S.filterKind ? { k: S.filterKind, n: S.filter } : null;
  if (!f || !pins) return;
  if (f.k === 'country' || f.k === 'region') {
    const place = PLACES.find(p => p.k === f.k && p.n === f.n);
    const sites = sitesInPlace(f.n);
    if (place) {
      S.ring = ringFor(place, sites);
      S.ringCol = ringTint(CH.chapters[S.ch].color);
    }
    setFilter(f.n, sites, f.k);
    return;
  }
  const e = chapterIndex(CH.chapters[S.ch].id).find(x => x.k === f.k && x.n === f.n);
  setFilter(f.n, e ? e.sites : [], f.k);
}

function choose(i) {
  const e = results[i];
  if (!e) return;
  const d = chData[CH.chapters[S.ch].id];
  $('qres').classList.remove('on');
  $('q').blur();
  setPlay(false);

  if (e.k === 'country' || e.k === 'region') {
    let sites = sitesInPlace(e.n);
    if (alignAge(sites)) sites = sitesInPlace(e.n);
    S.ring = ringFor(e, sites);
    S.ringCol = ringTint(CH.chapters[S.ch].color);
    /* frame the ring rather than a fixed zoom, so a country and a county both fit */
    flyTo(e.lon, e.lat, e.p, zoomForRadius(S.ring.rad));
    setFilter(e.n, sites, e.k);
    return;
  }
  S.ring = null;
  if (!d) return;
  const sites = e.k === 'locality' ? [e.site] : e.sites;
  if (!sites.length) {
    setFilter(e.n, [], e.k, e.occ
      ? `${e.n} — ${e.occ.toLocaleString()} records this period, none at a mapped site`
      : `${e.n} — not at any mapped locality here`);
    return;
  }
  alignAge(sites);
  /* aim at the richest site, so the view lands somewhere worth looking */
  let best = sites[0];
  for (const j of sites) if (d.sites.n[j] > d.sites.n[best]) best = j;
  flyTo(d.sites.lon[best], d.sites.lat[best], d.sites.plate[best],
        Math.max(S.zoom, e.k === 'locality' ? 4 : 2.6));
  setFilter(e.n, sites, e.k);
  if (e.k === 'locality' && pins) {
    const packed = pins.map.indexOf(e.site);
    if (packed >= 0) { S.sel = packed; showSite(packed); }
  }
}

/* ---------------------------------------------------------------- legend */
function syncLegend() {
  const d = chData[CH.chapters[S.ch].id];
  const box = $('lgbody');
  box.textContent = '';
  if (!d || !d.breakdown) { $('legend').classList.remove('on'); return; }
  d.breakdown.slice(0, 7).forEach(b => {
    const g = Math.min(b.g, 12);
    const r = el('div', 'lg' + (S.groupOn[g] ? '' : ' off'));
    const i = el('i');
    i.style.background = css(GROUP_COLOR[g]);
    r.appendChild(i);
    r.appendChild(el('span', null, d.groups[b.g]));
    r.onclick = () => {
      S.groupOn[g] = S.groupOn[g] ? 0 : 1;
      r.classList.toggle('off', !S.groupOn[g]);
      if (S.sel >= 0) { S.sel = -1; $('site').classList.remove('on'); }
    };
    box.appendChild(r);
  });
  $('legend').classList.add('on');
}

/* ------------------------------------------------------------ site popup */
function showSite(i) {
  const d = chData[pins.chapter];
  const src = pins.map[i], s = d.sites;
  $('sname').textContent = s.nm[src] || 'Unnamed locality';
  const bits = [];
  if (s.fm[src]) bits.push(s.fm[src] + (/formation|fm/i.test(s.fm[src]) ? '' : ' Formation'));
  bits.push(`${ageText(s.ea[src])} – ${ageText(s.la[src])}`);
  const place = d.locs && s.lc && s.lc[src] >= 0 ? d.locs[s.lc[src]] : '';
  bits.push((place ? place + ' — ' : '')
    + `${Math.abs(s.lat[src]).toFixed(1)}°${s.lat[src] >= 0 ? 'N' : 'S'}, `
    + `${Math.abs(s.lon[src]).toFixed(1)}°${s.lon[src] >= 0 ? 'E' : 'W'} today`);
  $('smeta').textContent = bits.join(' · ');
  const tx = s.tx[src] || [];
  $('scount').textContent = tx.length
    ? `${s.n[src]} taxa recorded${tx.length < s.n[src] ? `, first ${tx.length}` : ''}`
    : 'No taxon list for this locality';
  $('slist').innerHTML = tx.map(j => `<li>${d.names[j]}</li>`).join('');
  $('site').classList.add('on');
  $('legend').classList.remove('on');
}
function hideSite() {
  S.sel = -1;
  $('site').classList.remove('on');
  syncLegend();
}

/* --------------------------------------------------------- interactions */
let drag = null;
cv.addEventListener('pointerdown', e => {
  cv.setPointerCapture(e.pointerId);
  S.fly = null;
  drag = { x: e.clientX, y: e.clientY, moved: 0 };
  cv.classList.add('drag');
  S.spin = false; $('spin').classList.remove('on');
});
cv.addEventListener('pointermove', e => {
  if (!drag) return;
  const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
  drag.moved += Math.abs(dx) + Math.abs(dy);
  drag.x = e.clientX; drag.y = e.clientY;
  const k = 0.0052 / S.zoom;
  S.yaw -= dx * k * (cv.clientWidth / 600);
  S.pitch = clamp(S.pitch + dy * k * (cv.clientHeight / 600), -1.45, 1.45);
  $('hint').classList.add('gone');
});
cv.addEventListener('pointerup', e => {
  const wasDrag = drag && drag.moved > 6;
  drag = null;
  cv.classList.remove('drag');
  if (wasDrag) return;
  const r = cv.getBoundingClientRect();
  const hit = pick(e.clientX - r.left, e.clientY - r.top);
  if (hit >= 0) { S.sel = hit; showSite(hit); } else hideSite();
});
cv.addEventListener('pointercancel', () => { drag = null; cv.classList.remove('drag'); });

cv.addEventListener('wheel', e => {
  e.preventDefault();
  S.zoom = clamp(S.zoom * Math.exp(-e.deltaY * 0.0016), 1, 9);
  $('hint').classList.add('gone');
}, { passive: false });

/* pinch */
let pinch = null;
cv.addEventListener('touchstart', e => {
  if (e.touches.length === 2) {
    pinch = Math.hypot(e.touches[0].clientX - e.touches[1].clientX,
                       e.touches[0].clientY - e.touches[1].clientY);
    drag = null;
  }
}, { passive: true });
cv.addEventListener('touchmove', e => {
  if (e.touches.length === 2 && pinch) {
    e.preventDefault();
    const d = Math.hypot(e.touches[0].clientX - e.touches[1].clientX,
                         e.touches[0].clientY - e.touches[1].clientY);
    S.zoom = clamp(S.zoom * (d / pinch), 1, 9);
    pinch = d;
  }
}, { passive: false });
cv.addEventListener('touchend', () => { pinch = null; }, { passive: true });

$('zin').onclick = () => { S.zoom = clamp(S.zoom * 1.5, 1, 9); };
$('zout').onclick = () => { S.zoom = clamp(S.zoom / 1.5, 1, 9); };
$('spin').onclick = e => { S.spin = !S.spin; e.currentTarget.classList.toggle('on', S.spin); };
$('pins').onclick = e => {
  S.pins = !S.pins;
  e.currentTarget.classList.toggle('on', S.pins);
  if (!S.pins) hideSite();
};
$('sx').onclick = hideSite;

const qbox = $('q');
let qtimer = 0;
qbox.addEventListener('input', () => {
  $('qx').classList.toggle('on', !!qbox.value);
  clearTimeout(qtimer);
  qtimer = setTimeout(() => renderResults(search(qbox.value), qbox.value), 90);
});
qbox.addEventListener('focus', () => {
  if (qbox.value.trim().length >= 2) renderResults(search(qbox.value), qbox.value);
});
qbox.addEventListener('blur', () => setTimeout(() => $('qres').classList.remove('on'), 120));
qbox.addEventListener('keydown', e => {
  if (e.key === 'ArrowDown') { e.preventDefault(); highlightResult(1); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); highlightResult(-1); }
  else if (e.key === 'Enter') {
    e.preventDefault();
    clearTimeout(qtimer);
    /* Enter can beat the debounce, so make sure there is something to pick */
    if (!results.length) renderResults(search(qbox.value), qbox.value);
    choose(resultSel >= 0 ? resultSel : 0);
  }
  else if (e.key === 'Escape') { qbox.value = ''; $('qx').classList.remove('on'); $('qres').classList.remove('on'); qbox.blur(); }
});
$('qx').onclick = () => {
  qbox.value = '';
  $('qx').classList.remove('on');
  renderResults([], '');
  qbox.focus();
};
$('fclear').onclick = () => { setFilter(null, null); qbox.value = ''; $('qx').classList.remove('on'); };
$('ax').onclick = () => toggleAbout(false);

function setPlay(on) {
  S.play = on;
  $('playicon').innerHTML = on ? '<path d="M6 4h4v16H6zM14 4h4v16h-4z"/>' : '<path d="M7 4l13 8-13 8z"/>';
  $('play').setAttribute('aria-label', on ? 'Pause' : 'Play through time');
}
$('play').onclick = () => setPlay(!S.play);

/* rail scrubbing */
const track = $('track');
function railTo(clientX) {
  const r = track.getBoundingClientRect();
  const f = clamp((clientX - r.left) / r.width, 0, 1);
  let want = f * totalH, i = 0;
  while (i < sections.length - 1 && want > sections[i].h) { want -= sections[i].h; i++; }
  const s = sections[i];
  reader.scrollTop = s.top + want - reader.clientHeight * 0.42;
}
let railDrag = false;
track.addEventListener('pointerdown', e => {
  railDrag = true; setPlay(false);
  track.setPointerCapture(e.pointerId); railTo(e.clientX);
});
track.addEventListener('pointermove', e => {
  const r = track.getBoundingClientRect();
  const f = clamp((e.clientX - r.left) / r.width, 0, 1);
  let want = f * totalH, i = 0;
  while (i < sections.length - 1 && want > sections[i].h) { want -= sections[i].h; i++; }
  const s = sections[i];
  const c = s.ch, p = clamp(want / (s.h || 1), 0, 1);
  const tip = $('tip');
  tip.style.left = (f * 100) + '%';
  tip.textContent = `${c.name} · ${ageText(c.start + (c.end - c.start) * p)}`;
  if (railDrag) railTo(e.clientX);
});
track.addEventListener('pointerup', () => { railDrag = false; });

reader.addEventListener('scroll', () => { if (S.ready) onScroll(); }, { passive: true });
addEventListener('resize', () => { layout(); onScroll(); });
addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  if (e.key === ' ') { e.preventDefault(); setPlay(!S.play); }
  if (e.key === 'Escape') { hideSite(); toggleAbout(false); }
  if (e.key === '+' || e.key === '=') S.zoom = clamp(S.zoom * 1.4, 1, 9);
  if (e.key === '-') S.zoom = clamp(S.zoom / 1.4, 1, 9);
});

/* ------------------------------------------------------------------- boot */
async function boot() {
  const msg = $('loadmsg');
  const [chapters, meta, images, index, places] = await Promise.all([
    fetch(url('chapters.json')).then(r => r.json()),
    fetch(url('plates.json')).then(r => r.json()),
    fetch(url('images.json')).then(r => r.ok ? r.json() : {}).catch(() => ({})),
    fetch(url('ch/index.json')).then(r => r.ok ? r.json() : null).catch(() => null),
    fetch(url('places.json')).then(r => r.ok ? r.json() : []).catch(() => []),
  ]);
  CH = chapters; PL = meta; IMG = images || {}; chIndex = index;
  PLACES = (places || []).map(p => ({ ...p, k: p.k === 'country' ? 'country' : 'region' }));
  msg.textContent = 'Rotating the continents…';
  PL.buffer = await fetch(url('plates.bin')).then(r => r.arrayBuffer());

  buildRotations();
  initGL();
  buildReader();
  buildAbout();
  layout();
  S.ready = true;
  onScroll();
  poseAt(Math.min(S.t, PL.ageMax));
  requestAnimationFrame(frame);
  $('load').classList.add('done');
  setTimeout(() => $('load').remove(), 700);
  setTimeout(() => $('hint').classList.add('gone'), 9000);
  loadChapter(0); loadChapter(1);
  /* images finish arriving after first paint; the reader grows as they do */
  addEventListener('load', () => { layout(); onScroll(); });
  new ResizeObserver(() => { layout(); onScroll(); }).observe($('chapters'));
}

boot().catch(err => {
  console.error(err);
  $('loadmsg').textContent = 'Something went wrong loading the data: ' + err.message;
});
})();
