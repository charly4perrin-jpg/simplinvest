(() => {
  const canvas = document.getElementById('bg');
  const ctx = canvas.getContext('2d');
  const chapNum = document.getElementById('chapNum');
  const scrollHint = document.querySelector('.scroll-hint');
  const sections = [...document.querySelectorAll('.scene')];

  let W, H, DPR;
  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.width = window.innerWidth * DPR;
    H = canvas.height = window.innerHeight * DPR;
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
  }
  window.addEventListener('resize', resize);
  resize();

  let current = 'rain';
  let t = 0;

  // ---------- helpers ----------
  const rand = (a, b) => a + Math.random() * (b - a);
  function lerpColor(c1, c2, k) {
    return c1.map((v, i) => Math.round(v + (c2[i] - v) * k));
  }
  function grad(x0, y0, x1, y1, stops) {
    const g = ctx.createLinearGradient(x0, y0, x1, y1);
    stops.forEach(([o, c]) => g.addColorStop(o, c));
    return g;
  }

  // ---------- particle pools ----------
  const rainDrops = Array.from({ length: 140 }, () => ({
    x: rand(0, 1), y: rand(0, 1), len: rand(0.02, 0.08), spd: rand(0.006, 0.016),
    hue: Math.random() < 0.5 ? 'rgba(5,217,232,.55)' : 'rgba(255,110,199,.5)'
  }));

  const dots = Array.from({ length: 220 }, () => ({
    x: rand(0, 1), y: rand(0, 1), r: rand(0.5, 2.2), phase: rand(0, Math.PI * 2), spd: rand(0.4, 1.2)
  }));

  const palmSet = Array.from({ length: 6 }, (_, i) => ({
    x: (i + 0.5) / 6, scale: rand(0.7, 1.3), sway: rand(0, Math.PI * 2)
  }));

  const gridSpeedBase = 0.6;
  let gridOffset = 0;

  const pursuitStreaks = Array.from({ length: 40 }, () => ({
    y: rand(0, 1), len: rand(0.05, 0.22), spd: rand(0.01, 0.035), side: Math.random() < 0.5
  }));

  const spiralParticles = Array.from({ length: 260 }, (_, i) => ({
    a: (i / 260) * Math.PI * 2 * 6, r: rand(0.05, 1), spd: rand(0.15, 0.4)
  }));

  const skylineBuildings = Array.from({ length: 14 }, () => ({
    x: rand(0, 1), w: rand(0.02, 0.06), h: rand(0.15, 0.55)
  }));

  // ---------- scene renderers ----------
  function bgFill(colors) {
    ctx.fillStyle = grad(0, 0, 0, H, colors);
    ctx.fillRect(0, 0, W, H);
  }

  function drawRain() {
    bgFill([[0, '#0d0221'], [0.6, '#160636'], [1, '#0a0118']]);
    // faint skyline silhouette
    ctx.fillStyle = 'rgba(10,4,26,0.9)';
    ctx.beginPath();
    ctx.moveTo(0, H);
    for (let i = 0; i <= 10; i++) {
      const x = (i / 10) * W;
      const h = H * (0.18 + 0.12 * Math.abs(Math.sin(i * 1.7)));
      ctx.lineTo(x, H - h);
    }
    ctx.lineTo(W, H);
    ctx.closePath();
    ctx.fill();

    rainDrops.forEach(d => {
      d.y += d.spd;
      if (d.y > 1.1) d.y = -0.1;
      const x = d.x * W;
      const y = d.y * H;
      ctx.strokeStyle = d.hue;
      ctx.lineWidth = 1.4 * DPR;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x - 6 * DPR, y + d.len * H);
      ctx.stroke();
    });

    if (Math.sin(t * 0.02) > 0.985) {
      ctx.fillStyle = 'rgba(180,220,255,0.06)';
      ctx.fillRect(0, 0, W, H);
    }
  }

  function drawDots() {
    bgFill([[0, '#1a0933'], [1, '#2a0f4a']]);
    dots.forEach(d => {
      const flick = 0.5 + 0.5 * Math.sin(t * 0.03 * d.spd + d.phase);
      ctx.fillStyle = `rgba(255,${180 + flick * 60},${220 + flick * 30},${0.15 + flick * 0.5})`;
      ctx.beginPath();
      ctx.arc(d.x * W, d.y * H, d.r * DPR * (1 + flick * 0.5), 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function drawPalms() {
    bgFill([[0, '#ff9036'], [0.45, '#ff2e93'], [0.8, '#7b2ff7'], [1, '#170432']]);
    // sun
    const sunY = H * 0.42;
    const r = grad(0, sunY - H * 0.18, 0, sunY + H * 0.18, [[0, 'rgba(255,207,92,.95)'], [1, 'rgba(255,46,147,0)']]);
    ctx.fillStyle = r;
    ctx.beginPath();
    ctx.arc(W * 0.5, sunY, H * 0.18, 0, Math.PI * 2);
    ctx.fill();
    // horizon line stripes (retro sun)
    ctx.strokeStyle = 'rgba(20,5,40,0.5)';
    for (let i = 0; i < 6; i++) {
      const y = sunY + H * 0.02 * i * i * 0.4;
      ctx.lineWidth = 2 * DPR;
      ctx.beginPath();
      ctx.moveTo(W * 0.5 - H * 0.18, y);
      ctx.lineTo(W * 0.5 + H * 0.18, y);
      ctx.stroke();
    }
    // palms silhouette
    ctx.fillStyle = 'rgba(10,3,20,0.92)';
    palmSet.forEach(p => {
      const sway = Math.sin(t * 0.01 + p.sway) * 6;
      const x = p.x * W;
      const baseY = H;
      const trunkH = H * 0.32 * p.scale;
      ctx.save();
      ctx.translate(x, baseY);
      ctx.rotate(sway * Math.PI / 180 * 0.02);
      ctx.fillRect(-3 * DPR, -trunkH, 6 * DPR, trunkH);
      for (let a = 0; a < 6; a++) {
        const ang = (a / 6) * Math.PI * 2;
        ctx.save();
        ctx.translate(0, -trunkH);
        ctx.rotate(ang + sway * 0.02);
        ctx.beginPath();
        ctx.ellipse(28 * DPR * p.scale, 0, 34 * DPR * p.scale, 8 * DPR * p.scale, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
      ctx.restore();
    });
  }

  function drawGrid() {
    bgFill([[0, '#170432'], [1, '#050112']]);
    const horizon = H * 0.55;
    // sun glow
    ctx.fillStyle = grad(0, horizon - H * 0.15, 0, horizon, [[0, 'rgba(255,46,147,.5)'], [1, 'rgba(255,46,147,0)']]);
    ctx.fillRect(0, horizon - H * 0.15, W, H * 0.15);

    gridOffset += gridSpeedBase * DPR;
    ctx.strokeStyle = 'rgba(5,217,232,.55)';
    ctx.lineWidth = 1.2 * DPR;
    const vanishX = W / 2;
    for (let i = -12; i <= 12; i++) {
      const x0 = vanishX + i * 60 * DPR;
      ctx.beginPath();
      ctx.moveTo(vanishX, horizon);
      ctx.lineTo(x0, H);
      ctx.stroke();
    }
    const rows = 14;
    for (let i = 0; i < rows; i++) {
      const prog = ((i + (gridOffset / (40 * DPR)) % 1) / rows);
      const y = horizon + Math.pow(prog, 2.2) * (H - horizon);
      ctx.globalAlpha = 0.15 + prog * 0.6;
      ctx.beginPath();
      ctx.moveTo(vanishX - (y - horizon) * 1.6, y);
      ctx.lineTo(vanishX + (y - horizon) * 1.6, y);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  function drawPursuit() {
    bgFill([[0, '#0a0118'], [1, '#170225']]);
    const flash = Math.floor(t * 0.08) % 2 === 0;
    ctx.fillStyle = flash ? 'rgba(255,30,60,0.10)' : 'rgba(20,80,255,0.12)';
    ctx.fillRect(0, 0, W, H);

    pursuitStreaks.forEach(s => {
      s.y -= s.spd;
      if (s.y < -0.1) s.y = 1.1;
      const y = s.y * H;
      const color = s.side ? 'rgba(255,60,90,.5)' : 'rgba(60,160,255,.5)';
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5 * DPR;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(s.len * W, y);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(W, y + 20 * DPR);
      ctx.lineTo(W - s.len * W, y + 20 * DPR);
      ctx.stroke();
    });
  }

  function drawCellbars() {
    const pulse = 0.5 + 0.5 * Math.sin(t * 0.03);
    bgFill([[0, `rgba(255,${140 + pulse * 40},60,1)`], [0.5, '#ff2e93'], [1, '#170225']]);
    // radial glow center
    const g = ctx.createRadialGradient(W / 2, H * 0.45, 0, W / 2, H * 0.45, H * 0.6);
    g.addColorStop(0, `rgba(255,235,190,${0.5 + pulse * 0.3})`);
    g.addColorStop(1, 'rgba(255,46,147,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    // bars
    ctx.fillStyle = 'rgba(5,2,15,0.85)';
    const barCount = 9;
    for (let i = 0; i < barCount; i++) {
      const x = (i / barCount) * W;
      ctx.fillRect(x, 0, W * 0.015, H);
    }
  }

  function drawSpiral() {
    bgFill([[0, '#050014'], [1, '#0d0221']]);
    ctx.save();
    ctx.translate(W / 2, H / 2);
    const maxR = Math.min(W, H) * 0.62;
    const arms = 3;
    const rotation = t * 0.006;

    // glowing spiral arms (log-spiral tunnel look)
    for (let arm = 0; arm < arms; arm++) {
      const armOffset = (arm / arms) * Math.PI * 2;
      for (let pass = 0; pass < 2; pass++) {
        ctx.beginPath();
        const steps = 140;
        for (let i = 0; i <= steps; i++) {
          const k = i / steps;
          const theta = k * Math.PI * 5 + armOffset + rotation * (pass === 0 ? 1 : -0.6);
          const rad = maxR * Math.pow(k, 0.82);
          const x = Math.cos(theta) * rad;
          const y = Math.sin(theta) * rad;
          if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        const c = pass === 0 ? [255, 110, 199] : [5, 217, 232];
        ctx.strokeStyle = `rgba(${c[0]},${c[1]},${c[2]},${pass === 0 ? 0.55 : 0.35})`;
        ctx.lineWidth = (pass === 0 ? 2.4 : 1.4) * DPR;
        ctx.shadowColor = `rgba(${c[0]},${c[1]},${c[2]},0.8)`;
        ctx.shadowBlur = 14 * DPR;
        ctx.stroke();
      }
    }
    ctx.shadowBlur = 0;

    // inbound particles riding the arms
    spiralParticles.forEach(p => {
      p.a += 0.006 + (1 - p.r) * 0.015;
      p.r -= 0.0016;
      if (p.r < 0.015) p.r = 1;
      const rad = maxR * Math.pow(p.r, 0.82);
      const x = Math.cos(p.a + rotation) * rad;
      const y = Math.sin(p.a + rotation) * rad;
      const k = 1 - p.r;
      const c = lerpColor([255, 207, 92], [5, 217, 232], k);
      ctx.fillStyle = `rgba(${c[0]},${c[1]},${c[2]},${0.25 + k * 0.7})`;
      ctx.beginPath();
      ctx.arc(x, y, (1 + k * 2.8) * DPR, 0, Math.PI * 2);
      ctx.fill();
    });

    // bright vortex core
    const core = ctx.createRadialGradient(0, 0, 0, 0, 0, maxR * 0.12);
    core.addColorStop(0, 'rgba(255,240,220,0.9)');
    core.addColorStop(1, 'rgba(255,110,199,0)');
    ctx.fillStyle = core;
    ctx.beginPath();
    ctx.arc(0, 0, maxR * 0.12, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  function drawSkyline() {
    bgFill([[0, '#0d0221'], [0.5, '#1a0933'], [1, '#2a0a3d']]);
    // moon
    ctx.fillStyle = grad(0, H * 0.15, 0, H * 0.45, [[0, 'rgba(5,217,232,.85)'], [1, 'rgba(123,47,247,0)']]);
    ctx.beginPath();
    ctx.arc(W * 0.78, H * 0.22, H * 0.14, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = 'rgba(8,2,20,0.95)';
    skylineBuildings.forEach(b => {
      const x = b.x * W;
      const w = b.w * W;
      const h = b.h * H;
      ctx.fillRect(x, H - h, w, h);
      // windows
      ctx.fillStyle = 'rgba(255,110,199,0.5)';
      for (let wy = H - h + 10 * DPR; wy < H - 6 * DPR; wy += 14 * DPR) {
        for (let wx = x + 4 * DPR; wx < x + w - 4 * DPR; wx += 10 * DPR) {
          if (Math.random() < 0.3) ctx.fillRect(wx, wy, 3 * DPR, 5 * DPR);
        }
      }
      ctx.fillStyle = 'rgba(8,2,20,0.95)';
    });
    // ground grid reflection
    ctx.strokeStyle = 'rgba(5,217,232,.35)';
    ctx.lineWidth = 1 * DPR;
    for (let i = 0; i < 8; i++) {
      const y = H - i * 8 * DPR;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }
  }

  function drawLogo() {
    bgFill([[0, '#0d0221'], [1, '#1a0933']]);
    const pulse = 0.5 + 0.5 * Math.sin(t * 0.025);
    const g = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, Math.max(W, H) * 0.5);
    g.addColorStop(0, `rgba(255,110,199,${0.25 + pulse * 0.15})`);
    g.addColorStop(0.5, `rgba(5,217,232,${0.1 + pulse * 0.1})`);
    g.addColorStop(1, 'rgba(13,2,33,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  const renderers = {
    rain: drawRain, dots: drawDots, palms: drawPalms, grid: drawGrid,
    pursuit: drawPursuit, cellbars: drawCellbars, spiral: drawSpiral,
    skyline: drawSkyline, logo: drawLogo
  };

  function loop() {
    t++;
    (renderers[current] || drawRain)();
    requestAnimationFrame(loop);
  }
  loop();

  // ---------- scroll-driven chapter switching ----------
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const inner = entry.target.querySelector('.scene-inner');
      entry.target.classList.toggle('active', entry.isIntersecting && entry.intersectionRatio > 0.5);
      if (inner) inner.classList.toggle('in-view', entry.intersectionRatio > 0.35);

      if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
        const scene = entry.target.dataset.scene;
        const idx = sections.indexOf(entry.target) + 1;
        if (scene !== current) {
          canvas.style.opacity = 0.4;
          setTimeout(() => { canvas.style.opacity = 1; }, 260);
        }
        current = scene;
        chapNum.textContent = String(idx).padStart(2, '0');
        window.setActive3DScene?.(scene);
      }
    });
  }, { threshold: [0, 0.35, 0.5, 1] });

  sections.forEach(s => io.observe(s));

  window.addEventListener('scroll', () => {
    scrollHint.classList.toggle('hide', window.scrollY > 80);
  });

  // ---------- 3D cursor tilt on the active chapter's text block ----------
  window.addEventListener('pointermove', (e) => {
    const activeSection = document.querySelector('.scene.active');
    if (!activeSection) return;
    const inner = activeSection.querySelector('.scene-inner');
    if (!inner) return;
    const nx = (e.clientX / window.innerWidth - 0.5) * 2;
    const ny = (e.clientY / window.innerHeight - 0.5) * 2;
    inner.style.setProperty('--tiltX', `${nx * 4}deg`);
    inner.style.setProperty('--tiltY', `${-ny * 3}deg`);
  });

  document.getElementById('restart').addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();
