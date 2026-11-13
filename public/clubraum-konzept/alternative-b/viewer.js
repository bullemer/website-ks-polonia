// Alternative B – Clubraum in drei Bereichen (Croatia | Polonia | gemeinsam).
// Maße identisch mit scripts/build_grundriss_3bereiche.py (Grundriss B-04):
// Ursprung linke obere Innenecke, x nach rechts, z plan-abwärts, y nach oben, Meter.
import * as THREE from 'three';
import { OrbitControls } from './vendor/OrbitControls.js';
import { GLTFExporter } from './vendor/GLTFExporter.js';

const W = 11.55, D = 11.10, AW = 4.40, AD = 4.44, MID = W / 2, ZONE = 8.15;
const COLS = [[4.532, 5.6], [7.717, 5.6]];
const TOP = 0.93;
const HALL_WIN = { center: 3.9, width: 2.2, height: 2.05, sill: 0.925 };
const C = {
  floor: '#b9b8ae', wall: '#cfccc0', wallDark: '#9b9d91', oak: '#b88a55', charcoal: '#3a3637',
  cream: '#ece6d6', croBlue: '#2a4a8f', croRed: '#c8102e', polRed: '#ab293d', wine: '#7a2232',
  felt: '#5d6b63', steel: '#2f3433', planter: '#3d4240', leaf: '#4f7a44', leaf2: '#3e6a3a',
};
const mirror = x => 2 * MID - x;
const $ = s => document.querySelector(s);
const status = $('#status');

const view = $('#viewport');
const scene = new THREE.Scene();
scene.background = new THREE.Color('#e7e8df');
const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 150);
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
view.prepend(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.maxDistance = 45;
controls.maxPolarAngle = Math.PI / 2 - 0.02;

scene.add(new THREE.HemisphereLight(0xffffff, 0x8b8b73, 2.4));
const sun = new THREE.DirectionalLight(0xfff1d9, 2.6);
sun.position.set(-6, 18, 14);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, far: 60 });
sun.shadow.bias = -0.0005;
sun.target.position.set(5.8, 0, 7.5);
scene.add(sun, sun.target);

const model = new THREE.Group();
model.name = 'Clubraum_Alternative_B_drei_Bereiche';
model.userData = { status: 'Konzept, Aufmaß erforderlich', units: 'metres', plan: 'Grundriss B-04' };
scene.add(model);
const groups = {};
for (const n of ['base', 'zones', 'routes', 'shared', 'croatia', 'polonia', 'divider', 'lights', 'roof', 'labels']) {
  groups[n] = new THREE.Group();
  groups[n].name = n;
  model.add(groups[n]);
}
groups.routes.visible = false;
groups.roof.visible = false;

// ---------------------------------------------------------------- Helfer
const mats = {};
function mat(c, opts = {}) {
  const key = c + JSON.stringify(opts);
  return mats[key] ??= new THREE.MeshStandardMaterial({ color: c, roughness: 0.85, ...opts });
}
function box(g, name, x, y, z, w, h, d, c, opts) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), typeof c === 'string' ? mat(c, opts) : c);
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  m.name = name;
  g.add(m);
  return m;
}
// Box über Planecken (x0,z0)-(x1,z1), Unterkante y0, Höhe h
function block(g, name, x0, z0, x1, z1, y0, h, c, opts) {
  return box(g, name, (x0 + x1) / 2, y0 + h / 2, (z0 + z1) / 2, x1 - x0, h, z1 - z0, c, opts);
}
function cyl(g, name, x, y, z, r, h, c, rTop = r) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(rTop, r, h, 28), mat(c));
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  m.name = name;
  g.add(m);
  return m;
}
function canvasTex(w, h, draw) {
  const cv = document.createElement('canvas');
  cv.width = w; cv.height = h;
  draw(cv.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}
function plane(g, name, tex, x, y, z, w, h, ry = 0, basic = true) {
  const material = basic ? new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide })
    : new THREE.MeshStandardMaterial({ map: tex, roughness: 0.8, side: THREE.DoubleSide });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), material);
  m.position.set(x, y, z);
  m.rotation.y = ry;
  m.name = name;
  g.add(m);
  return m;
}
const checker = (nx, ny) => canvasTex(nx * 32, ny * 32, (ctx) => {
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    ctx.fillStyle = (i + j) % 2 ? '#ffffff' : C.croRed;
    ctx.fillRect(i * 32, j * 32, 32, 32);
  }
});
function textTex(lines, bg, fg, w = 1024, h = 256) {
  return canvasTex(w, h, (ctx) => {
    ctx.fillStyle = bg; ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = fg; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    lines.forEach(([t, size, dy = 0]) => {
      ctx.font = `bold ${size}px "DejaVu Sans", Arial`;
      ctx.fillText(t, w / 2, h / 2 + dy, w * 0.94);
    });
  });
}
function label(text, sub, color, x, y, z, scale = 1) {
  const tex = canvasTex(1024, 300, (ctx, w, h) => {
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.beginPath(); ctx.roundRect(8, 8, w - 16, h - 16, 40); ctx.fill();
    ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.font = 'bold 120px "DejaVu Sans", Arial'; ctx.fillText(text, w / 2, 120, w - 60);
    ctx.font = '58px "DejaVu Sans", Arial'; ctx.fillText(sub, w / 2, 225, w - 60);
  });
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true }));
  s.scale.set(3.0 * scale, 0.88 * scale, 1);
  s.position.set(x, y, z);
  s.renderOrder = 10;
  s.name = 'Label ' + text;
  groups.labels.add(s);
}

// ---------------------------------------------------------------- Bestand
const B = groups.base;
block(B, 'Boden Hauptraum', 0, 0, W, D, -0.26, 0.26, C.floor);
block(B, 'Boden Nische', 0, D, AW, D + AD, -0.26, 0.26, C.floor);
// Nordwand voll hoch (TV-Wand beider Vereine) mit Fenster 8,10–10,20
block(B, 'Nordwand West', -0.24, -0.24, 8.1, 0, 0, 3.6, C.wall);
block(B, 'Nordwand Ost', 10.2, -0.24, W + 0.24, 0, 0, 3.6, C.wall);
block(B, 'Nordwand Brüstung', 8.1, -0.24, 10.2, 0, 0, 0.9, C.wall);
block(B, 'Nordwand Sturz', 8.1, -0.24, 10.2, 0, 2.95, 0.65, C.wall);
const glass = new THREE.MeshStandardMaterial({ color: '#aac6c7', transparent: true, opacity: 0.25, roughness: 0.15, side: THREE.DoubleSide });
block(B, 'Fenster Nord', 8.1, -0.14, 10.2, -0.1, 0.9, 2.05, glass);
block(B, 'Heizkörper Nord', 8.15, 0.05, 10.15, 0.2, 0.22, 0.55, '#e8e7dd');
// Westwand: Außenfenster mit Brüstung 0,87 m
block(B, 'Westwand Brüstung', -0.24, 0, 0, D + AD, 0, 0.87, C.wall);
block(B, 'Westwand Sturz', -0.24, 0, 0, D + AD, 2.95, 0.65, C.wall);
const winW = [[1.65, 2.35], [4.65, 2.35], [7.65, 2.35], [10.3, 1.1], [12.5, 1.6]];
let zPrev = 0;
for (const [zc, len] of winW) {
  block(B, 'Fensterpfeiler', -0.24, zPrev, 0, zc - len / 2, 0.87, 2.08, C.wall);
  block(B, 'Fenster West', -0.16, zc - len / 2, -0.12, zc + len / 2, 0.87, 2.08, glass);
  block(B, 'Heizkörper', 0.05, zc - len * 0.42, 0.2, zc + len * 0.42, 0.2, 0.58, '#e8e7dd');
  zPrev = zc + len / 2;
}
block(B, 'Fensterpfeiler', -0.24, zPrev, 0, D + AD, 0.87, 2.08, C.wall);
// Ostwand zur Sporthalle mit Sichtfenster (ballwurfsicher)
const hz0 = HALL_WIN.center - HALL_WIN.width / 2, hz1 = HALL_WIN.center + HALL_WIN.width / 2;
block(B, 'Ostwand', W, 0, W + 0.24, hz0, 0, 3.6, C.wall);
block(B, 'Ostwand', W, hz1, W + 0.24, D, 0, 3.6, C.wall);
block(B, 'Ostwand Brüstung', W, hz0, W + 0.24, hz1, 0, HALL_WIN.sill, C.wall);
block(B, 'Ostwand Sturz', W, hz0, W + 0.24, hz1, HALL_WIN.sill + HALL_WIN.height, 3.6 - HALL_WIN.sill - HALL_WIN.height, C.wall);
block(B, 'Sichtfenster Sporthalle', W + 0.1, hz0, W + 0.14, hz1, HALL_WIN.sill, HALL_WIN.height, glass);
plane(B, 'Schild Sporthalle', textTex([['SPORTHALLE', 130]], '#56796c', '#fff'), W - 0.01, 3.25, HALL_WIN.center, 1.9, 0.24, -Math.PI / 2);
// Südseite: Treppe/Luftraum – Wand als Schnitt 1,10 m, Tür Treppenhaus 10,35–11,55
block(B, 'Wand Treppe (Schnitt)', AW, D, 10.35, D + 0.24, 0, 1.1, C.wallDark);
block(B, 'Nischenwand Ost (Küche)', AW, D + 0.24, AW + 0.24, D + AD, 0, 2.4, C.wall);
block(B, 'Nischenwand Süd', 0, D + AD, 1.05, D + AD + 0.24, 0, 1.1, C.wall);
block(B, 'Nischenwand Süd', 2.45, D + AD, AW + 0.24, D + AD + 0.24, 0, 1.1, C.wall);
// Treppe / Luftraum (nicht Nutzfläche): Treppenlauf nach Osten ansteigend + Podest
const voidG = new THREE.Group(); voidG.name = 'Treppe / Luftraum'; B.add(voidG);
block(voidG, 'Luftraum Boden darunter', AW + 0.24, D + 0.24, W, D + AD, -3.3, 0.05, '#8d8f88');
for (let i = 0; i < 18; i++) {
  const x0 = 5.3 + i * 0.28;
  block(voidG, 'Stufe', x0 - 0.0, D + 0.24, x0 + 0.28, D + 1.68, -3.1 + i * 0.172, 0.172 + 0.05, '#a7a69c');
}
block(voidG, 'Podest', 10.35, D + 0.0, W, D + 1.68, -0.2, 0.2, '#a7a69c');
block(voidG, 'Geländer', 5.3, D + 1.7, W, D + 1.74, 0, 1.0, C.steel);
plane(B, 'Schild Ausgang 2', textTex([['AUSGANG 2 · TREPPENHAUS', 64]], '#337b50', '#fff'), 10.95, 2.3, D + 0.01, 1.0, 0.25, Math.PI);
plane(B, 'Schild Ausgang 1', textTex([['AUSGANG 1 · AUSSENTREPPE', 64]], '#337b50', '#fff'), 1.75, 2.3, D + AD + 0.25, 1.0, 0.25, Math.PI);
// Holzstützen 24/24 mit Stahlbetonsockel
for (const [x, z] of COLS) {
  box(B, 'Holzstütze 24/24', x, 2.2, z, 0.24, 4.4, 0.24, '#bd925e');
  box(B, 'Stützenfuß', x, 0.08, z, 0.27, 0.16, 0.27, '#71776e');
}
// Steigschacht-Öffnung + Brandschott (Lage lt. Plan, ca.)
block(B, 'Steigschacht + Brandschott (freihalten)', 1.6, 0, 2.2, 0.45, 0, 0.12, '#c8102e');
block(B, 'Steigschacht Verkleidung', 1.6, 0, 2.2, 0.45, 2.4, 1.2, '#d8d6cc');

// ---------------------------------------------------------------- Bodenzonen + Wege
const Z = groups.zones;
block(Z, 'Zone Croatia (leer)', 0, 0, MID, ZONE, 0, 0.006, '#dddbd4');
block(Z, 'Zone Polonia', MID, 0, W, ZONE, 0, 0.006, '#ecd0d4');
block(Z, 'Zone gemeinsam', 0, ZONE, W, D, 0, 0.004, '#d8d3c6');
block(Z, 'Zone gemeinsam Nische', 0, D, AW, D + AD, 0, 0.004, '#d8d3c6');
block(Z, 'Bereichsgrenze (Bodenmarkierung)', 0, ZONE - 0.03, W, ZONE + 0.03, 0, 0.009, '#4b5650');
const R = groups.routes;
const routeMat = new THREE.MeshBasicMaterial({ color: '#4fae7a', transparent: true, opacity: 0.38 });
block(R, 'Querweg 1,20 m', 0.75, ZONE, W, ZONE + 1.2, 0, 0.015, routeMat);
block(R, 'Weg Ausgang 2', 10.35, ZONE + 1.2, W, D, 0, 0.015, routeMat);
block(R, 'Weg Ausgang 1', 1.15, ZONE + 1.2, 2.35, D + AD, 0, 0.015, routeMat);

// ---------------------------------------------------------------- Vereinsbereiche (gespiegelt)
const logoTex = await new THREE.TextureLoader().loadAsync('./assets/original-logo.png');
logoTex.colorSpace = THREE.SRGBColorSpace;
function logo(g, x, y, z, w, ry) {
  const h = w * logoTex.image.height / logoTex.image.width;
  return plane(g, 'Original KS Polonia Wappen', logoTex, x, y, z, w, h, ry);
}
const chairMat = C.cream;
function chair(g, x, z, facing) { // facing: +1 = Blick nach +z
  block(g, 'Stuhl Sitz', x - 0.22, z - 0.22, x + 0.22, z + 0.22, 0.43, 0.04, chairMat);
  const bz = z - facing * 0.2;
  block(g, 'Stuhl Lehne', x - 0.21, bz - 0.02, x + 0.21, bz + 0.02, 0.47, 0.42, chairMat);
  for (const dx of [-0.18, 0.18]) for (const dz of [-0.18, 0.18]) cyl(g, 'Stuhlbein', x + dx, 0.215, z + dz, 0.015, 0.43, C.steel);
}
function table(g, x0, z0, x1, z1) {
  block(g, 'Tischplatte Eiche', x0, z0, x1, z1, 0.72, 0.04, C.oak);
  for (const x of [x0 + 0.08, x1 - 0.08]) for (const z of [z0 + 0.08, z1 - 0.08]) block(g, 'Tischbein', x - 0.025, z - 0.025, x + 0.025, z + 0.025, 0, 0.72, C.steel);
}
function sofa(g, x0, z0, x1, z1, c, backAt) { // backAt: 'n' | 's' | 'w' | 'e'
  block(g, 'Polster Sitz', x0, z0, x1, z1, 0.1, 0.34, c);
  const t = 0.18;
  const back = { n: [x0, z0, x1, z0 + t], s: [x0, z1 - t, x1, z1], w: [x0, z0, x0 + t, z1], e: [x1 - t, z0, x1, z1] }[backAt];
  block(g, 'Polster Lehne', ...back, 0.1, 0.72, c);
  const arms = (backAt === 'n' || backAt === 's') ? [[x0, z0, x0 + 0.16, z1], [x1 - 0.16, z0, x1, z1]] : [[x0, z0, x1, z0 + 0.16], [x0, z1 - 0.16, x1, z1]];
  for (const a of arms) block(g, 'Polster Armlehne', ...a, 0.1, 0.52, c);
  block(g, 'Sockel', x0 + 0.05, z0 + 0.05, x1 - 0.05, z1 - 0.05, 0, 0.1, C.charcoal);
}
function clubArea(side) {
  const g = groups[side];
  const m = side === 'croatia' ? (x => x) : mirror;
  const span = (a, b) => [Math.min(m(a), m(b)), Math.max(m(a), m(b))];
  const accent = side === 'croatia' ? C.croBlue : C.polRed;
  const lounge = side === 'croatia' ? '#2c477f' : C.wine;
  // Lowboard + TV 75" + Soundbar
  const [lb0, lb1] = span(3.60, 5.60);
  block(g, 'Lowboard', lb0, 0.05, lb1, 0.5, 0.08, 0.42, C.charcoal);
  block(g, 'Lowboard Deckplatte', lb0, 0.05, lb1, 0.5, 0.5, 0.03, C.oak);
  const tvx = (lb0 + lb1) / 2;
  box(g, 'TV 75 Zoll', tvx, 1.55, 0.05, 1.68, 0.97, 0.06, '#121816');
  const screen = side === 'croatia'
    ? textTex([['CROATIA', 150, -20], ['MATCHDAY', 70, 95]], '#1b2d5a', '#ffffff', 1024, 592)
    : textTex([['POLONIA', 150, -20], ['MATCHDAY', 70, 95]], '#4a1a24', '#ffffff', 1024, 592);
  plane(g, 'TV Bild', screen, tvx, 1.55, 0.085, 1.62, 0.92, 0);
  box(g, 'Soundbar', tvx, 0.98, 0.07, 0.95, 0.07, 0.08, '#20272a');
  // Wandgestaltung über dem TV: Croatia Schachbrettband, Polonia Wappen auf Vereinsrot
  if (side === 'croatia') {
    plane(g, 'Wandband Schachbrett', checker(12, 2), tvx, 2.55, 0.012, 2.4, 0.4, 0, false);
    plane(g, 'Schriftzug Croatia', textTex([['CROATIA', 150]], '#ffffff', C.croBlue), tvx, 2.98, 0.012, 1.6, 0.4, 0);
  } else {
    plane(g, 'Wandfläche Vereinsrot', textTex([['', 10]], C.polRed, '#fff', 64, 64), tvx, 2.75, 0.012, 2.4, 0.95, 0, false);
    logo(g, tvx, 2.75, 0.02, 0.62, 0);
  }
  // Vereinsschrank abschließbar
  const [hs0, hs1] = span(0.30, 1.50);
  block(g, 'Vereinsschrank abschließbar', hs0, 0.05, hs1, 0.65, 0, 2.1, C.charcoal);
  block(g, 'Schrank Front', hs0 + 0.02, 0.65, hs1 - 0.02, 0.67, 0.06, 1.98, '#4a4648');
  // Lounge: Sofa + 2 Sessel Richtung TV
  const [so0, so1] = span(3.60, 5.60);
  sofa(g, so0, 3.0, so1, 3.9, lounge, 's');
  for (const sz of [2.10, 3.15]) {
    const [a0, a1] = span(2.60, 3.40);
    sofa(g, a0, sz, a1, sz + 0.8, lounge, side === 'croatia' ? 'w' : 'e');
  }
  const [ct0, ct1] = span(3.95, 5.25);
  block(g, 'Couchtisch', ct0, 2.2, ct1, 2.75, 0.0, 0.42, C.oak);
  // Zwei Tische 1,60 × 0,80 mit je 6 Stühlen
  for (const tz of [1.60, 4.80]) {
    const [t0, t1] = span(0.80, 2.40);
    table(g, t0, tz, t1, tz + 0.8);
    for (const cx of [1.10, 1.60, 2.10]) {
      chair(g, m(cx), tz - 0.35, +1);
      chair(g, m(cx), tz + 1.15, -1);
    }
  }
  // Teppich unter der Lounge in Vereinsfarbe
  const [r0, r1] = span(2.45, 5.55);
  block(g, 'Teppich Lounge', r0, 1.95, r1, 4.05, 0.006, 0.012, side === 'croatia' ? '#8fa2c9' : '#c99aa2');
  void accent;
}
// Croatia-Bereich bleibt leer und neutral – Einrichtung durch Croatia.
clubArea('polonia');
logo(groups.polonia, 8.55, 0.012, 6.75, 0.9, 0).rotation.set(-Math.PI / 2, 0, 0);
groups.polonia.children.at(-1).name = 'Bodenmarke Polonia';
groups.polonia.children.at(-1).position.y = 0.013;

// ---------------------------------------------------------------- Zwei Pantryküchen; ehemalige Thekenfläche bleibt frei
const S = groups.shared;
for (const {name, start, sink, storage, hob} of [
  {name: 'Croatia', start: 11.25, sink: 12.45, storage: 11.85, hob: 11.25},
  {name: 'Polonia', start: 13.05, sink: 13.05, storage: 13.65, hob: 14.25},
]) {
  // Drei 60-cm-Module je Pantry. Das Kochfeld ist mobil; die Platte bleibt frei.
  for (const [z0, kind] of [[sink, 'Spülenunterschrank'], [storage, 'Stauraum/Abfall'], [hob, 'Freie Kochfeldposition']]) {
    block(S, `${name} ${kind}`, 3.71, z0, 4.35, z0 + 0.60, 0, TOP - 0.04, C.charcoal);
    block(S, `${name} ${kind} Front`, 3.698, z0 + 0.02, 3.71, z0 + 0.58, 0.05, 0.79,
      kind === 'Stauraum/Abfall' ? '#625c57' : '#4a4648');
  }
  block(S, `${name} Arbeitsplatte`, 3.68, start + 0.01, 4.36, start + 1.79, TOP - 0.04, 0.04, C.oak);
  block(S, `${name} Spüle`, 3.82, sink + 0.08, 4.22, sink + 0.52, TOP - 0.01, 0.02,
    '#c9cfd1', {metalness: 0.6, roughness: 0.3});
  block(S, `${name} Spülbecken`, 3.86, sink + 0.12, 4.18, sink + 0.48, TOP + 0.011, 0.004, '#72858a');
  cyl(S, `${name} Ablauf`, 4.02, TOP + 0.017, sink + 0.30, 0.018, 0.004, '#d8dfe0');
  cyl(S, `${name} Armatur`, 4.27, TOP + 0.15, sink + 0.30, 0.015, 0.3, '#c9cfd1');
  box(S, `${name} Armatur Auslauf`, 4.18, TOP + 0.29, sink + 0.30, 0.18, 0.02, 0.02, '#c9cfd1');
  block(S, `${name} Wandschrank`, 3.84, storage + 0.02, 4.37, storage + 0.58, 1.55, 0.70, '#4a4648');
  block(S, `${name} Wandschrank Tür`, 3.82, storage + 0.04, 3.84, storage + 0.56, 1.59, 0.62, C.cream);
  block(S, `${name} Spritzschutz`, 4.36, start, 4.40, start + 1.80, TOP, 0.62, '#e2dfd6');
}
block(S, 'Trennwand zwischen den Pantrys', 2.90, 13.03, 4.40, 13.07, 0, 2.30, C.wallDark);
// Getränkekühlschränke K1 Croatia / K2 Polonia (Glastür nach Osten)
for (const [z0, name, c] of [[11.50, 'K1 Croatia', null], [13.75, 'K2 Polonia', C.polRed]]) {
  block(S, 'Getränkekühlschrank ' + name, 0.08, z0, 0.70, z0 + 0.6, 0, 1.85, '#e9ecec');
  block(S, name + ' Glastür', 0.70, z0 + 0.04, 0.72, z0 + 0.56, 0.12, 1.55, glass);
  if (c) plane(S, name + ' Schild', textTex([[name.split(' ')[1].toUpperCase(), 120]], c, '#fff', 512, 160), 0.725, 1.76, z0 + 0.3, 0.5, 0.15, Math.PI / 2);
  for (let i = 0; i < 4; i++) block(S, 'Flaschenreihe', 0.15, z0 + 0.08, 0.66, z0 + 0.52, 0.25 + i * 0.36, 0.22, i % 2 ? '#7b5b2a' : '#3d6b3a');
}
block(S, 'RWA-Taster 1 (freihalten)', 0, 13.0, 0.06, 13.22, 1.2, 0.22, '#c8102e');

// ---------------------------------------------------------------- Mobile Trennung
const DV = groups.divider;
const dividerModes = {};
function panel(g, z0, idx) {
  const z1 = z0 + 1.18;
  block(g, `Stellwand ${idx} Akustikfilz`, MID - 0.04, z0, MID + 0.04, z1, 0.12, 1.9, C.felt);
  block(g, `Stellwand ${idx} Band Polonia`, MID + 0.04, z0, MID + 0.045, z1, 1.82, 0.12, C.polRed);
  for (const z of [z0 + 0.12, z1 - 0.12]) {
    block(g, 'Fuß', MID - 0.22, z - 0.03, MID + 0.22, z + 0.03, 0.04, 0.04, C.steel);
    for (const x of [MID - 0.18, MID + 0.18]) cyl(g, 'Rolle mit Bremse', x, 0.035, z, 0.035, 0.03, '#222');
    block(g, 'Ständer', MID - 0.015, z - 0.015, MID + 0.015, z + 0.015, 0.06, 0.08, C.steel);
  }
}
function planter(g, z0, idx) {
  const z1 = z0 + 1.18;
  block(g, `Pflanzkübel ${idx}`, MID - 0.22, z0, MID + 0.22, z1, 0.05, 0.5, C.planter);
  for (const z of [z0 + 0.12, z1 - 0.12]) for (const x of [MID - 0.17, MID + 0.17]) cyl(g, 'Rolle', x, 0.03, z, 0.03, 0.04, '#222');
  block(g, 'Erde', MID - 0.2, z0 + 0.02, MID + 0.2, z1 - 0.02, 0.55, 0.01, '#4a3a2a');
  // drei Pflanzen je Kübel, unterschiedliche Höhe (ca. 1,5–1,9 m)
  [0.22, 0.59, 0.96].forEach((dz, k) => {
    const h = [1.55, 1.85, 1.65][(k + idx) % 3];
    cyl(g, 'Stamm', MID, 0.55 + (h - 0.55) / 2, z0 + dz, 0.02, h - 0.55, '#6b5136');
    const leafMat = mat(k % 2 ? C.leaf : C.leaf2);
    for (let j = 0; j < 4; j++) {
      const s = new THREE.Mesh(new THREE.IcosahedronGeometry(0.2 + 0.05 * ((j + k) % 3), 1), leafMat);
      s.position.set(MID + (j % 2 ? 0.1 : -0.1), h - 0.15 * j, z0 + dz + (j % 3 - 1) * 0.08);
      s.castShadow = true; s.name = 'Blattwerk';
      g.add(s);
    }
  });
}
for (const mode of ['walls', 'plants', 'mix', 'open']) {
  const g = new THREE.Group();
  g.name = 'Trennung ' + mode;
  DV.add(g);
  dividerModes[mode] = g;
  for (let i = 0; i < 6; i++) {
    const z0 = 0.10 + i * 1.20;
    if (mode === 'walls' || (mode === 'mix' && i < 4)) panel(g, z0, i + 1);
    else if (mode === 'plants' || mode === 'mix') planter(g, z0, i + 1);
  }
  if (mode === 'open') {
    // 6 Stellwände an der Nordwand zusammengeschoben (Parkposition)
    for (let i = 0; i < 6; i++) {
      const x = MID - 0.25 + i * 0.1;
      block(g, `Stellwand ${i + 1} geparkt`, x - 0.04, 0.65, x + 0.04, 1.83, 0.12, 1.9, C.felt);
    }
    block(g, 'Parkposition Fußplatte', MID - 0.3, 0.65, MID + 0.3, 1.83, 0.0, 0.06, C.steel);
  }
}
const dividerNotes = {
  walls: '6 freistehende Akustik-Stellwände à 1,20 m, ca. 2,0 m hoch, auf Rollen mit Bremse. Beidseitig Filz, Polonia-Seite mit Band in Vereinsrot.',
  plants: '6 Pflanzkübel auf Rollen à 1,20 × 0,45 m im selben Raster. Durchlässiger, wohnlicher – weniger Sicht- und Schallschutz, Pflege nötig.',
  mix: '4 Stellwände im Lounge-/TV-Bereich (Sicht- und Schallschutz), 2 Pflanzkübel zum gemeinsamen Bereich hin.',
  open: 'Gemeinsames Event: Stellwände an der Nordwand zusammengeschoben – ein großer, offener Raum.',
};
function setDivider(mode) {
  for (const [k, g] of Object.entries(dividerModes)) g.visible = k === mode;
  $('#divider-note').textContent = dividerNotes[mode];
  for (const b of document.querySelectorAll('#dividers button')) b.classList.toggle('active', b.dataset.divider === mode);
  state.divider = mode;
}

// ---------------------------------------------------------------- Leuchten + Dach
const L = groups.lights;
const lampMat = new THREE.MeshStandardMaterial({ color: '#fff3d6', emissive: '#ffe2a8', emissiveIntensity: 1.2 });
for (const x of [2.9, 8.65]) for (const z of [1.6, 4.0, 6.4]) {
  box(L, 'LED-Linienleuchte (Bereich)', x, 3.65, z, 1.2, 0.05, 0.12, '#1c1f1e');
  box(L, 'Lichtaustritt', x, 3.62, z, 1.14, 0.01, 0.08, lampMat);
  for (const d of [-0.4, 0.4]) box(L, 'Abhängung', x + d, 4.2, z, 0.012, 1.1, 0.012, '#3d4440');
}
for (const z of [11.6, 13.4]) {
  box(L, 'Küchenleuchte', 3.9, 2.7, z, 0.12, 0.05, 1.1, '#1c1f1e');
  box(L, 'Lichtaustritt', 3.9, 2.67, z, 0.08, 0.01, 1.04, lampMat);
}
const RF = groups.roof;
box(RF, 'Holzpfette 24/45 (Annahme)', MID, 4.4, COLS[0][1], W, 0.45, 0.24, '#b78b57');
for (const x of [1.5, 3.5, 5.5, 7.5, 9.5]) box(RF, 'Nebenträger Holz', x, 4.75, D / 2, 0.15, 0.26, D, '#c59b67');
for (let x = 0.3; x < W; x += 0.3) box(RF, 'Trapezblech', x, 4.9, D / 2, 0.065, 0.04, D, '#afb5ad');
box(RF, 'Oberlicht', 7.75, 4.95, 7.95, 0.6, 0.02, 1.3, glass);

// ---------------------------------------------------------------- Beschriftung
label('CROATIA', 'Bereich frei · 47,1 m²', '#6b736d', 2.9, 3.4, 4.2);
label('POLONIA', 'Vereinsbereich · 47,1 m²', C.polRed, 8.65, 3.4, 4.2);
label('GEMEINSAM', 'Freifläche · Küche · 53,6 m²', '#5d5446', 9.4, 2.6, 9.85, 0.85);

// ---------------------------------------------------------------- Kamera
const state = { divider: 'walls', view: 'overview' };
const views = {
  overview: [[6.0, 13.5, 23.5], [5.8, 0.2, 6.4]],
  croatia: [[5.0, 2.6, 7.6], [2.6, 1.0, 1.8]],
  polonia: [[6.6, 2.6, 7.6], [9.0, 1.0, 1.8]],
  shared: [[3.4, 2.7, 6.3], [6.0, 0.6, 10.1]],
  pantryCroatia: [[1.35, 2.65, 11.25], [3.8, 1.35, 12.1]],
  pantryPolonia: [[1.35, 2.65, 14.65], [3.8, 1.35, 14.0]],
  kitchen: [[2.2, 2.6, 15.3], [2.4, 0.8, 11.2]],
  top: [[5.8, 26, 7.85], [5.8, 0, 7.75]],
};
function setView(name) {
  const [p, t] = views[name];
  controls.minDistance = name === 'overview' || name === 'top' ? 4 : 0.5;
  const aspect = view.clientWidth / Math.max(1, view.clientHeight);
  const k = (name === 'overview' || name === 'top') && aspect < 1.2 ? 1.45 : 1;
  camera.position.set(t[0] + (p[0] - t[0]) * k, t[1] + (p[1] - t[1]) * k, t[2] + (p[2] - t[2]) * k);
  controls.target.set(...t);
  if (name === 'top') camera.position.z += 0.01;
  controls.update();
  for (const b of document.querySelectorAll('#views button')) b.classList.toggle('active', b.dataset.view === name);
  state.view = name;
}
for (const b of document.querySelectorAll('#views button')) b.onclick = () => setView(b.dataset.view);
for (const b of document.querySelectorAll('#dividers button')) b.onclick = () => setDivider(b.dataset.divider);
const toggles = { 't-labels': 'labels', 't-zones': 'zones', 't-routes': 'routes', 't-lights': 'lights', 't-roof': 'roof' };
for (const [id, g] of Object.entries(toggles)) {
  $('#' + id).onchange = e => { groups[g].visible = e.target.checked; };
  groups[g].visible = $('#' + id).checked;
}

$('#export').onclick = () => {
  const labelsWere = groups.labels.visible;
  groups.labels.visible = false; // Sprites nicht exportieren
  new GLTFExporter().parse(model, (glb) => {
    groups.labels.visible = labelsWere;
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([glb], { type: 'model/gltf-binary' }));
    a.download = `clubraum-alternative-b-${state.divider}.glb`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  }, (err) => { groups.labels.visible = labelsWere; alert('Export fehlgeschlagen: ' + err); }, { binary: true, onlyVisible: true });
};

function resize() {
  const w = view.clientWidth, h = view.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(view);
resize();
setDivider('walls');
setView('overview');
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
status.textContent = 'Konzeptmodell · Maße lt. Grundriss B-04 · vor Ort prüfen';
window.alternativeB = { scene, model, camera, controls, renderer, setView, setDivider, groups, ready: true };
