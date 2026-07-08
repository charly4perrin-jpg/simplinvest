import * as THREE from './vendor/three.module.js';

const COLORS = {
  pink: 0xff2e93,
  hotPink: 0xff6ec7,
  cyan: 0x05d9e8,
  teal: 0x00fff0,
  orange: 0xff9036,
  gold: 0xffcf5c,
  purple: 0x7b2ff7,
  ink: 0xf5f0ff,
};

const canvas = document.getElementById('bg3d');
const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 60);
camera.position.set(0, 0, 5);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ---------- fade bookkeeping: each material remembers its target group + resting opacity ----------
const fadeList = []; // { mat, group, base }
function fade(mat, group) {
  fadeList.push({ mat, group, base: mat.opacity });
  mat.opacity = 0;
  return mat;
}

function glowTexture(hex, hardness = 0.15) {
  const size = 256;
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d');
  const color = new THREE.Color(hex);
  const r = Math.round(color.r * 255), g = Math.round(color.g * 255), b = Math.round(color.b * 255);
  const grad = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  grad.addColorStop(0, `rgba(${r},${g},${b},1)`);
  grad.addColorStop(hardness, `rgba(${r},${g},${b},.6)`);
  grad.addColorStop(1, `rgba(${r},${g},${b},0)`);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);
  return new THREE.CanvasTexture(c);
}

function glowSprite(hex, scale = 3, hardness) {
  const mat = new THREE.SpriteMaterial({
    map: glowTexture(hex, hardness), transparent: true,
    blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.9
  });
  const s = new THREE.Sprite(mat);
  s.scale.set(scale, scale, 1);
  return s;
}

function neonEdge(mesh, group, color, opacity = 0.9) {
  const edges = new THREE.EdgesGeometry(mesh.geometry);
  const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity, depthWrite: false });
  const line = new THREE.LineSegments(edges, fade(mat, group));
  mesh.add(line);
  return line;
}

function solidMesh(geo, group, color = 0x0a0316, opacity = 0.92) {
  const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity, depthWrite: false });
  return new THREE.Mesh(geo, fade(mat, group));
}

// ================= HERO GROUPS =================
const groups = {};

// --- 1. rain / PROLOGUE : portal rings + distant wireframe towers ---
{
  const g = new THREE.Group();
  groups.rain = g;
  const ring1 = solidMesh(new THREE.TorusGeometry(1.15, 0.03, 8, 80), g);
  neonEdge(ring1, g, COLORS.hotPink, 0.85);
  ring1.position.z = -2.2;
  const ring2 = solidMesh(new THREE.TorusGeometry(0.85, 0.02, 8, 80), g);
  neonEdge(ring2, g, COLORS.cyan, 0.6);
  ring2.position.z = -2.2;
  g.add(ring1, ring2);
  g.userData.spin = [ring1, ring2];

  for (let i = 0; i < 9; i++) {
    const h = 0.6 + Math.random() * 1.6;
    const box = solidMesh(new THREE.BoxGeometry(0.35, h, 0.35), g);
    neonEdge(box, g, i % 2 === 0 ? COLORS.pink : COLORS.cyan, 0.35);
    box.position.set((i - 4) * 0.55, -1.1 + h / 2, -5.5 + Math.random() * 1.5);
    g.add(box);
  }
  scene.add(g);
}

// --- 2. dots / ENCOUNTER : two orbiting figures + connecting glow line ---
{
  const g = new THREE.Group();
  groups.dots = g;
  const a = solidMesh(new THREE.IcosahedronGeometry(0.32, 0), g);
  neonEdge(a, g, COLORS.hotPink);
  const b = solidMesh(new THREE.IcosahedronGeometry(0.32, 0), g);
  neonEdge(b, g, COLORS.cyan);
  g.add(a, b);

  const lineGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
  const lineMat = fade(new THREE.LineBasicMaterial({ color: COLORS.ink, transparent: true, opacity: 0.35, depthWrite: false }), g);
  const line = new THREE.Line(lineGeo, lineMat);
  g.add(line);

  g.userData.orbit = { a, b, line };
  scene.add(g);
}

// --- 3. palms / SUNSET STRIP : low-poly palm row + sun ---
{
  const g = new THREE.Group();
  groups.palms = g;
  const sun = glowSprite(COLORS.gold, 4.5, 0.25);
  fade(sun.material, g);
  sun.position.set(0, 0.6, -4);
  g.add(sun);

  function palm(scale) {
    const p = new THREE.Group();
    const trunk = solidMesh(new THREE.CylinderGeometry(0.05, 0.09, 1.5, 6), g);
    neonEdge(trunk, g, COLORS.pink, 0.4);
    trunk.position.y = 0.75;
    p.add(trunk);
    for (let i = 0; i < 6; i++) {
      const frond = solidMesh(new THREE.ConeGeometry(0.42, 0.12, 4), g);
      neonEdge(frond, g, COLORS.hotPink, 0.5);
      frond.position.y = 1.5;
      frond.rotation.z = Math.PI / 2.4;
      frond.rotation.y = (i / 6) * Math.PI * 2;
      p.add(frond);
    }
    p.scale.setScalar(scale);
    return p;
  }
  const palms = [];
  for (let i = 0; i < 5; i++) {
    const p = palm(0.7 + Math.random() * 0.5);
    p.position.set((i - 2) * 0.9, -1.2, -1.5 - Math.random());
    palms.push(p);
    g.add(p);
  }
  g.userData.palms = palms;
  scene.add(g);
}

// --- 4. grid / THE JOB : 3D floor grid + rotating diamond ---
{
  const g = new THREE.Group();
  groups.grid = g;
  const grid = new THREE.GridHelper(14, 22, COLORS.pink, COLORS.cyan);
  grid.position.y = -1.3;
  grid.material.transparent = true;
  grid.material.depthWrite = false;
  fade(grid.material, g);
  g.add(grid);

  const diamond = solidMesh(new THREE.OctahedronGeometry(0.55, 0), g);
  neonEdge(diamond, g, COLORS.gold, 1);
  diamond.position.set(0, 0.3, -1.5);
  g.add(diamond);
  g.userData.spin = [diamond];
  scene.add(g);
}

// --- 5. pursuit / PURSUIT : low-poly car speeding toward camera ---
{
  const g = new THREE.Group();
  groups.pursuit = g;
  const car = new THREE.Group();
  const body = solidMesh(new THREE.BoxGeometry(1.1, 0.32, 0.55), g);
  neonEdge(body, g, COLORS.cyan);
  const cabin = solidMesh(new THREE.BoxGeometry(0.55, 0.28, 0.5), g);
  neonEdge(cabin, g, COLORS.hotPink);
  cabin.position.set(-0.05, 0.28, 0);
  car.add(body, cabin);
  [[-0.38, 0.28], [0.38, 0.28], [-0.38, -0.28], [0.38, -0.28]].forEach(([x, z]) => {
    const wheel = solidMesh(new THREE.CylinderGeometry(0.16, 0.16, 0.12, 12), g);
    neonEdge(wheel, g, COLORS.pink, 0.6);
    wheel.rotation.x = Math.PI / 2;
    wheel.position.set(x, -0.15, z);
    car.add(wheel);
  });
  car.position.set(0, -0.6, -2.5);
  g.add(car);

  const glowRed = glowSprite(0xff2040, 3, 0.3);
  fade(glowRed.material, g);
  glowRed.position.set(-1.4, 0, -3);
  const glowBlue = glowSprite(0x2040ff, 3, 0.3);
  fade(glowBlue.material, g);
  glowBlue.position.set(1.4, 0, -3);
  g.add(glowRed, glowBlue);

  g.userData.car = car;
  g.userData.lights = [glowRed, glowBlue];
  scene.add(g);
}

// --- 6. cellbars / TRIAL : foreground bars + warm glow ---
{
  const g = new THREE.Group();
  groups.cellbars = g;
  const glow = glowSprite(COLORS.orange, 5, 0.3);
  fade(glow.material, g);
  glow.position.set(0, 0, -2.5);
  g.add(glow);

  for (let i = 0; i < 9; i++) {
    const bar = solidMesh(new THREE.CylinderGeometry(0.045, 0.045, 3, 8), g);
    neonEdge(bar, g, COLORS.gold, 0.55);
    bar.position.set((i - 4) * 0.42, 0, -0.6);
    g.add(bar);
  }
  scene.add(g);
}

// --- 7. spiral / SPIRAL : helix vortex particles ---
{
  const g = new THREE.Group();
  groups.spiral = g;
  const N = 500;
  const positions = new Float32Array(N * 3);
  const colors = new Float32Array(N * 3);
  const cPink = new THREE.Color(COLORS.hotPink);
  const cCyan = new THREE.Color(COLORS.cyan);
  for (let i = 0; i < N; i++) {
    const k = i / N;
    const angle = k * Math.PI * 10;
    const radius = 0.15 + k * 1.6;
    positions[i * 3] = Math.cos(angle) * radius;
    positions[i * 3 + 1] = Math.sin(angle) * radius;
    positions[i * 3 + 2] = -k * 6;
    const c = cPink.clone().lerp(cCyan, k);
    colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const mat = fade(new THREE.PointsMaterial({
    size: 0.05, vertexColors: true, transparent: true, opacity: 0.9,
    blending: THREE.AdditiveBlending, depthWrite: false
  }), g);
  const points = new THREE.Points(geo, mat);
  g.add(points);
  g.userData.helix = points;
  scene.add(g);
}

// --- 8. skyline / VICE : city block + moon ---
{
  const g = new THREE.Group();
  groups.skyline = g;
  const moon = glowSprite(COLORS.cyan, 3.5, 0.3);
  fade(moon.material, g);
  moon.position.set(1.3, 1, -4);
  g.add(moon);

  for (let i = 0; i < 12; i++) {
    const h = 0.5 + Math.random() * 1.8;
    const box = solidMesh(new THREE.BoxGeometry(0.4, h, 0.4), g);
    neonEdge(box, g, i % 3 === 0 ? COLORS.hotPink : COLORS.cyan, 0.5);
    box.position.set((i - 5.5) * 0.5, -1.2 + h / 2, -2 - Math.random() * 3);
    g.add(box);
  }
  scene.add(g);
}

// --- 9. logo / EPILOGUE : rotating hero car + orbiting ring particles ---
{
  const g = new THREE.Group();
  groups.logo = g;
  const hero = new THREE.Group();
  const body = solidMesh(new THREE.BoxGeometry(1.3, 0.36, 0.62), g);
  neonEdge(body, g, COLORS.hotPink);
  const cabin = solidMesh(new THREE.BoxGeometry(0.62, 0.3, 0.56), g);
  neonEdge(cabin, g, COLORS.gold);
  cabin.position.set(-0.05, 0.32, 0);
  hero.add(body, cabin);
  [[-0.45, 0.32], [0.45, 0.32], [-0.45, -0.32], [0.45, -0.32]].forEach(([x, z]) => {
    const wheel = solidMesh(new THREE.CylinderGeometry(0.18, 0.18, 0.14, 12), g);
    neonEdge(wheel, g, COLORS.cyan, 0.7);
    wheel.rotation.x = Math.PI / 2;
    wheel.position.set(x, -0.16, z);
    hero.add(wheel);
  });
  hero.position.set(0, 1.7, -3.4);
  hero.rotation.y = 0.6;
  g.add(hero);

  const ringN = 140;
  const ringPos = new Float32Array(ringN * 3);
  for (let i = 0; i < ringN; i++) {
    const a = (i / ringN) * Math.PI * 2;
    ringPos[i * 3] = Math.cos(a) * 1.6;
    ringPos[i * 3 + 1] = Math.sin(a) * 0.5 + 1.7;
    ringPos[i * 3 + 2] = -3.4 + Math.sin(a * 3) * 0.3;
  }
  const ringGeo = new THREE.BufferGeometry();
  ringGeo.setAttribute('position', new THREE.BufferAttribute(ringPos, 3));
  const ringMat = fade(new THREE.PointsMaterial({ color: COLORS.cyan, size: 0.045, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending, depthWrite: false }), g);
  const ring = new THREE.Points(ringGeo, ringMat);
  g.add(ring);

  g.userData.hero = hero;
  g.userData.ring = ring;
  scene.add(g);
}

let activeScene = 'rain';
export function setActive3DScene(name) {
  if (groups[name]) activeScene = name;
}
window.setActive3DScene = setActive3DScene;

// ---------- mouse parallax ----------
let mouseX = 0, mouseY = 0, targetX = 0, targetY = 0;
window.addEventListener('pointermove', (e) => {
  targetX = (e.clientX / window.innerWidth - 0.5) * 2;
  targetY = (e.clientY / window.innerHeight - 0.5) * 2;
});

const clock = new THREE.Clock();
let lastScrollY = window.scrollY;
let scrollVel = 0;

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  // scroll-scrub: velocity rolls the camera, page progress dollies it
  const sy = window.scrollY;
  scrollVel += ((sy - lastScrollY) - scrollVel) * 0.1;
  lastScrollY = sy;
  const frac = window.__scrollFrac ?? 0;

  mouseX += (targetX - mouseX) * 0.04;
  mouseY += (targetY - mouseY) * 0.04;
  camera.position.x += (mouseX * 0.4 - camera.position.x) * 0.05;
  camera.position.y += (-mouseY * 0.25 - camera.position.y) * 0.05;
  camera.position.z = 5 - Math.sin(frac * Math.PI) * 0.5;
  camera.lookAt(0, 0, -1.5);
  camera.rotation.z = THREE.MathUtils.clamp(scrollVel * 0.0006, -0.05, 0.05);

  fadeList.forEach(({ mat, group, base }) => {
    const target = group === groups[activeScene] ? base : 0;
    mat.opacity += (target - mat.opacity) * 0.18;
  });

  if (groups.rain.userData.spin) groups.rain.userData.spin.forEach((r, i) => { r.rotation.z += dt * (i === 0 ? 0.15 : -0.22); });

  const orbit = groups.dots.userData.orbit;
  if (orbit) {
    const r = 0.9;
    orbit.a.position.set(Math.cos(time * 0.6) * r, Math.sin(time * 0.6) * r * 0.6, -1.8);
    orbit.b.position.set(Math.cos(time * 0.6 + Math.PI) * r, Math.sin(time * 0.6 + Math.PI) * r * 0.6, -1.8);
    const pos = orbit.line.geometry.attributes.position;
    pos.setXYZ(0, orbit.a.position.x, orbit.a.position.y, orbit.a.position.z);
    pos.setXYZ(1, orbit.b.position.x, orbit.b.position.y, orbit.b.position.z);
    pos.needsUpdate = true;
  }

  if (groups.palms.userData.palms) {
    groups.palms.userData.palms.forEach((p, i) => { p.rotation.z = Math.sin(time * 0.8 + i) * 0.05; });
  }

  if (groups.grid.userData.spin) groups.grid.userData.spin.forEach(d => {
    d.rotation.y += dt * 0.6; d.rotation.x += dt * 0.3; d.position.y = 0.3 + Math.sin(time * 1.2) * 0.08;
  });

  if (groups.pursuit.userData.car) {
    const car = groups.pursuit.userData.car;
    car.position.z = -2.5 + ((time * 1.4) % 3);
    if (activeScene === 'pursuit') {
      groups.pursuit.userData.lights.forEach((l, i) => {
        const flash = Math.sin(time * 6 + i * Math.PI) > 0 ? 1 : 0.15;
        const base = fadeList.find(f => f.mat === l.material)?.base ?? 0.9;
        l.material.opacity += (base * flash - l.material.opacity) * 0.3;
      });
    }
  }

  if (groups.spiral.userData.helix) {
    groups.spiral.userData.helix.rotation.z += dt * 0.25;
    groups.spiral.userData.helix.position.z = (time * 0.4) % 6;
  }

  if (groups.skyline) groups.skyline.rotation.y = Math.sin(time * 0.05) * 0.05;

  if (groups.logo.userData.hero) {
    groups.logo.userData.hero.rotation.y += dt * 0.35;
    groups.logo.userData.ring.rotation.z += dt * 0.2;
  }

  renderer.render(scene, camera);
}
animate();
