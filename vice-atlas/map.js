(() => {
  // ---------- data ----------
  const CATS = {
    histoire:    { label: 'Histoire',     color: '#ff6ec7' },
    braquage:    { label: 'Braquage',     color: '#ffcf5c' },
    collectible: { label: 'Collectible',  color: '#05d9e8' },
    secret:      { label: 'Secret',       color: '#b96bff' },
    activite:    { label: 'Activité',     color: '#ff9036' },
  };

  const POIS = {
    v: [
      { name: 'Mont Chiliad', cat: 'secret', x: 305, y: 118, premium: true,
        desc: 'Le sommet de San Andreas et sa fameuse fresque. Téléphérique, rampes de saut, et un mystère que la communauté gratte depuis 2013.' },
      { name: 'Paleto Bay', cat: 'braquage', x: 330, y: 70,
        desc: 'Petite ville côtière du nord. Théâtre du braquage le plus musclé de l\'histoire : la banque du comté de Blaine.' },
      { name: 'Alamo Sea', cat: 'activite', x: 400, y: 295,
        desc: 'Mer intérieure salée. Jet-ski, épaves et couchers de soleil toxiques. Base idéale pour explorer le désert.' },
      { name: 'Sandy Shores', cat: 'histoire', x: 452, y: 330,
        desc: 'Le fief de Trevor Philips. Caravanes, laboratoire, et le pire voisinage de l\'État.' },
      { name: 'Fort Zancudo', cat: 'secret', x: 230, y: 386, premium: true,
        desc: 'Base militaire. Y entrer = 4 étoiles immédiates. Le hangar cache l\'un des jets les plus rapides du jeu. Itinéraire d\'infiltration inclus.' },
      { name: 'Observatoire de Galileo', cat: 'collectible', x: 355, y: 640,
        desc: 'Vue panoramique sur la ville, spots de photo et une pièce cachée sur le toit du dôme.' },
      { name: 'Vinewood Sign', cat: 'collectible', x: 400, y: 668,
        desc: 'Les lettres mythiques des collines. Un jeton de casino est planqué derrière le W.' },
      { name: 'Diamond Casino', cat: 'braquage', x: 505, y: 726, premium: true,
        desc: 'Le braquage aux trois approches. Fiche complète : équipages, points d\'entrée, découpe des parts et sorties de secours.' },
      { name: 'Maze Bank Tower', cat: 'activite', x: 462, y: 800,
        desc: 'Le plus haut gratte-ciel de Los Santos. Point de départ des sauts en parachute les plus vertigineux.' },
      { name: 'Del Perro Pier', cat: 'activite', x: 292, y: 812,
        desc: 'Grande roue, stands et arnaques en bord de mer. Une épave de collectible dort sous les pilotis.' },
      { name: 'Aéroport LSIA', cat: 'histoire', x: 395, y: 918,
        desc: 'Portes de la ville. Missions d\'ouverture et hangar de contrebande à débloquer.' },
      { name: 'Humane Labs', cat: 'braquage', x: 615, y: 585, premium: true,
        desc: 'Laboratoire ultra-sécurisé au bord de la mer. Le raid de nuit avec vision thermique, étape par étape.' },
      { name: 'Phare d\'El Gordo', cat: 'secret', x: 648, y: 468,
        desc: 'Falaises de l\'est. Point de départ d\'une chasse au trésor en 3 étapes.' },
    ],
    vi: [
      { name: 'Ocean Drive', cat: 'histoire', x: 636, y: 400,
        desc: 'Le front de mer art déco de Vice City. Néons roses, voitures de collection et gros ennuis en perspective.' },
      { name: 'Vice Beach', cat: 'activite', x: 648, y: 480,
        desc: 'La plage la plus célèbre de Leonida. Muscle beach, paddle et fêtes qui débordent jusqu\'au matin.' },
      { name: 'Downtown Vice', cat: 'braquage', x: 618, y: 340, premium: true,
        desc: 'Tours de verre et chambres fortes. Notre première fiche braquage de Leonida — mise à jour à chaque nouvelle info officielle.' },
      { name: 'Leonida Keys', cat: 'histoire', x: 560, y: 940,
        desc: 'Chapelet d\'îles au sud. Ponts interminables, criques de contrebandiers et le calme avant la tempête.' },
      { name: 'Grassrivers', cat: 'secret', x: 235, y: 445, premium: true,
        desc: 'Les marais de Leonida. Alligators, hydroglisseurs et légendes locales — la communauté a déjà repéré 3 zones étranges dans les trailers.' },
      { name: 'Port Gellhorn', cat: 'histoire', x: 285, y: 660,
        desc: 'Ville portuaire décatie de la côte ouest. Motels, casses automobiles et économie parallèle.' },
      { name: 'Mount Kalaga', cat: 'activite', x: 368, y: 95,
        desc: 'Parc national du nord. Pistes de trail, points de vue et cabanes perdues dans la brume.' },
      { name: 'Ambrosia', cat: 'braquage', x: 392, y: 430,
        desc: 'Ville industrielle au milieu des champs de canne. Raffinerie, trains de marchandises... et convoyeurs de fonds.' },
      { name: 'Hangar 13 — rumeur', cat: 'secret', x: 330, y: 545, premium: true,
        desc: 'Aérodrome repéré image par image dans le trailer 2. Non confirmé par Rockstar — fiche sourcée avec captures et timecodes.' },
      { name: 'Marina de Vice', cat: 'activite', x: 600, y: 555,
        desc: 'Yachts, jet-skis et courses nocturnes entre les pontons. Le spot de départ idéal pour explorer la baie.' },
    ],
  };

  // ---------- state ----------
  const body = document.body;
  let world = location.hash === '#leonida' ? 'vi' : 'v';
  let activeCats = new Set(Object.keys(CATS));
  let query = '';
  let selected = null;

  // progression tracker (persisted per world, keyed by POI name)
  const doneSets = { v: null, vi: null };
  ['v', 'vi'].forEach(w => {
    try { doneSets[w] = new Set(JSON.parse(localStorage.getItem('atlas_done_' + w) || '[]')); }
    catch { doneSets[w] = new Set(); }
  });
  function saveDone(w) {
    try { localStorage.setItem('atlas_done_' + w, JSON.stringify([...doneSets[w]])); } catch {}
  }

  // ---------- dom ----------
  const tabs = { v: document.getElementById('tab-v'), vi: document.getElementById('tab-vi') };
  const maps = { v: document.getElementById('mapV'), vi: document.getElementById('mapVI') };
  const markerLayers = { v: document.getElementById('markersV'), vi: document.getElementById('markersVI') };
  const chipsBox = document.getElementById('chips');
  const list = document.getElementById('poiList');
  const countEl = document.getElementById('poiCount');
  const legend = document.getElementById('legend');
  const card = document.getElementById('poiCard');
  const cardName = document.getElementById('cardName');
  const cardCat = document.getElementById('cardCat');
  const cardDesc = document.getElementById('cardDesc');
  const cardLock = document.getElementById('cardLock');
  const cardVisit = document.getElementById('cardVisit');
  const progLabel = document.getElementById('progLabel');
  const progPct = document.getElementById('progPct');
  const progFill = document.getElementById('progFill');

  // ---------- build chips + legend ----------
  Object.entries(CATS).forEach(([key, c]) => {
    const chip = document.createElement('button');
    chip.className = 'chip on';
    chip.style.setProperty('--chip-color', c.color);
    chip.innerHTML = `<i></i>${c.label}`;
    chip.addEventListener('click', () => {
      if (activeCats.has(key) && activeCats.size === 1) {
        activeCats = new Set(Object.keys(CATS)); // re-enable all when toggling last one
      } else if (activeCats.has(key)) {
        activeCats.delete(key);
      } else {
        activeCats.add(key);
      }
      chipsBox.querySelectorAll('.chip').forEach((el, i) =>
        el.classList.toggle('on', activeCats.has(Object.keys(CATS)[i])));
      render();
    });
    chipsBox.appendChild(chip);

    const lg = document.createElement('span');
    lg.innerHTML = `<i style="--c:${c.color}"></i>${c.label}`;
    legend.appendChild(lg);
  });

  // ---------- SVG markers ----------
  const NS = 'http://www.w3.org/2000/svg';
  function buildMarkers(w) {
    const layer = markerLayers[w];
    layer.innerHTML = '';
    POIS[w].forEach((p, i) => {
      const g = document.createElementNS(NS, 'g');
      g.setAttribute('class', 'marker');
      g.setAttribute('transform', `translate(${p.x},${p.y})`);
      g.style.setProperty('--c', CATS[p.cat].color);
      g.dataset.idx = i;

      const pulse = document.createElementNS(NS, 'circle');
      pulse.setAttribute('class', 'pulse');
      pulse.setAttribute('r', 7);
      pulse.style.animationDelay = `${(i % 5) * 0.4}s`;
      const dot = document.createElementNS(NS, 'circle');
      dot.setAttribute('class', 'dot');
      dot.setAttribute('r', 6.5);
      const label = document.createElementNS(NS, 'text');
      label.setAttribute('x', 12);
      label.setAttribute('y', 4);
      label.textContent = p.name.toUpperCase();
      g.append(pulse, dot, label);

      if (p.premium) {
        const lock = document.createElementNS(NS, 'text');
        lock.setAttribute('class', 'lockglyph');
        lock.setAttribute('x', -3.5);
        lock.setAttribute('y', -10);
        lock.textContent = '◆';
        g.appendChild(lock);
      }

      g.addEventListener('click', () => select(w, i));
      layer.appendChild(g);
    });
  }
  buildMarkers('v');
  buildMarkers('vi');

  // ---------- render (filter application) ----------
  function visible(p) {
    return activeCats.has(p.cat) &&
      (!query || p.name.toLowerCase().includes(query));
  }

  function render() {
    const pois = POIS[world];
    const done = doneSets[world];
    let shown = 0;

    markerLayers[world].querySelectorAll('.marker').forEach((g, i) => {
      const ok = visible(pois[i]);
      g.style.display = ok ? '' : 'none';
      g.classList.toggle('sel', selected === i);
      g.classList.toggle('done', done.has(pois[i].name));
      if (ok) shown++;
    });

    list.innerHTML = '';
    pois.forEach((p, i) => {
      if (!visible(p)) return;
      const li = document.createElement('li');
      li.style.setProperty('--c', CATS[p.cat].color);
      li.classList.toggle('sel', selected === i);
      li.classList.toggle('done', done.has(p.name));
      li.innerHTML = `<i></i><span class="nm">${p.name}</span>` +
        (done.has(p.name) ? '<span class="tick">✓</span>' : '') +
        (p.premium ? '<span class="lock">◆ PASS</span>' : '');
      li.addEventListener('click', () => select(world, i));
      list.appendChild(li);
    });

    countEl.textContent = `${shown} lieu${shown > 1 ? 'x' : ''} affiché${shown > 1 ? 's' : ''}`;

    const total = pois.length;
    const doneCount = pois.filter(p => done.has(p.name)).length;
    const pct = total ? Math.round((doneCount / total) * 100) : 0;
    progLabel.textContent = `${doneCount} / ${total} explorés`;
    progPct.textContent = `${pct}%`;
    progFill.style.width = `${pct}%`;
  }

  // ---------- selection / detail card ----------
  function select(w, i) {
    selected = i;
    const p = POIS[w][i];
    cardName.textContent = p.name;
    cardCat.textContent = CATS[p.cat].label + (p.premium ? ' — Vice Pass' : '');
    cardDesc.textContent = p.desc;
    cardLock.hidden = !p.premium;
    updateVisitBtn(p);
    card.hidden = false;
    render();
  }

  function updateVisitBtn(p) {
    const isDone = doneSets[world].has(p.name);
    cardVisit.textContent = isDone ? '✓ Visité — annuler' : 'Marquer comme visité';
    cardVisit.classList.toggle('is-done', isDone);
  }

  cardVisit.addEventListener('click', () => {
    if (selected === null) return;
    const p = POIS[world][selected];
    const done = doneSets[world];
    done.has(p.name) ? done.delete(p.name) : done.add(p.name);
    saveDone(world);
    updateVisitBtn(p);
    render();
  });
  document.getElementById('cardClose').addEventListener('click', () => {
    card.hidden = true;
    selected = null;
    render();
  });

  // ---------- world switching ----------
  function setWorld(w) {
    world = w;
    selected = null;
    card.hidden = true;
    body.dataset.world = w;
    tabs.v.setAttribute('aria-selected', w === 'v');
    tabs.vi.setAttribute('aria-selected', w === 'vi');
    maps.v.classList.toggle('hidden', w !== 'v');
    maps.vi.classList.toggle('hidden', w !== 'vi');
    history.replaceState(null, '', w === 'vi' ? '#leonida' : '#los-santos');
    render();
  }
  tabs.v.addEventListener('click', () => setWorld('v'));
  tabs.vi.addEventListener('click', () => setWorld('vi'));

  // ---------- search ----------
  document.getElementById('poiSearch').addEventListener('input', (e) => {
    query = e.target.value.trim().toLowerCase();
    render();
  });

  setWorld(world);
})();
