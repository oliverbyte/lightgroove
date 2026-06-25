const apiBase = "__API_BASE__" || "";

const colors = {
  red: '#ef4444',
  green: '#22c55e',
  blue: '#3b82f6',
  white: '#e5e7eb',
  dimmer: '#f59e0b',
  shutter: '#94a3b8',
  macro: '#7c3aed',
  macro_speed: '#22d3ee',
  other: '#38bdf8',
};

async function post(url, body) {
  const res = await fetch(url, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body || {}) });
  return await res.json();
}

let isConnected = true;
let connectionCheckInterval;

async function checkConnection() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const response = await fetch(`${apiBase}/api/grandmaster`, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (response.ok && !isConnected) {
      isConnected = true;
      updateConnectionStatus();
      loadGrandmaster();
      loadBPM();
      loadFixtures();
      loadStaticColors();
    } else if (!response.ok && isConnected) {
      isConnected = false;
      updateConnectionStatus();
    }
  } catch (e) {
    if (isConnected) {
      isConnected = false;
      updateConnectionStatus();
    }
  }
}

function updateConnectionStatus() {
  const dot = document.getElementById('connection-dot');
  const text = document.getElementById('connection-text');

  if (isConnected) {
    dot.classList.remove('offline');
    text.textContent = 'Connected';
  } else {
    dot.classList.add('offline');
    text.textContent = 'Server Offline';
  }
}

connectionCheckInterval = setInterval(checkConnection, 3000);

function showToast(message, type = 'info', duration = 3000) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('removing');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

async function getStates() {
  const res = await fetch(`${apiBase}/api/states`);
  return await res.json();
}

function makeSlider(fixtureId, channelName, label, value, color, onChange) {
  const col = document.createElement('div');
  col.className = 'slider-col';
  col.dataset.fixtureId = fixtureId;
  col.dataset.channelName = channelName;
  const lab = document.createElement('label');
  lab.textContent = label;
  const input = document.createElement('input');
  input.type = 'range';
  input.min = '0';
  input.max = '255';
  input.step = '1';
  const initial = Math.round((value || 0) * 255);
  input.value = initial;
  if (color) input.style.accentColor = color;
  const out = document.createElement('output');
  out.textContent = initial.toString();
  input.addEventListener('input', () => {
    const dmx = Number(input.value);
    out.textContent = dmx.toString();
    onChange(dmx / 255);
  });
  col.appendChild(lab);
  col.appendChild(input);
  col.appendChild(out);
  return col;
}

function toLabel(name) {
  return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function renderFixtures(fixtures) {
  const grid = document.getElementById('fixtures-grid');
  grid.innerHTML = '';
  fixtures.forEach(fx => {
    const card = document.createElement('div');
    card.className = 'card';
    const h3 = document.createElement('h3');
    h3.innerHTML = `${fx.id} <span class="pill">${fx.type}</span> <span class="pill">U${fx.universe} @ ${fx.start_address}</span>`;
    card.appendChild(h3);

    const channels = fx.channels || [];
    const ordered = [...channels].sort((a, b) => (a.index ?? 0) - (b.index ?? 0) || a.name.localeCompare(b.name));

    const slots = document.createElement('div');
    slots.className = 'sliders';

    ordered.forEach(ch => {
      const accent = colors[ch.name] || colors[ch.type] || colors.other;
      const target = ch.name === 'dimmer'
        ? `${apiBase}/api/fixture/${fx.id}/dimmer`
        : `${apiBase}/api/fixture/${fx.id}/channel/${ch.name}`;
      slots.appendChild(
        makeSlider(fx.id, ch.name, toLabel(ch.name), 0, accent, v => post(target, { value: v }))
      );
    });

    card.appendChild(slots);
    grid.appendChild(card);
  });
}

async function loadFixtures() {
  const res = await fetch(`${apiBase}/api/fixtures`);
  const data = await res.json();
  renderFixtures(data.fixtures || []);
}

let midiLearning = false;
let midiLearningTarget = null;
let midiLearnPollId = null;

function setMidiLearning(active) {
  midiLearning = active;
  document.querySelectorAll('.midi-learn-btn').forEach(b => {
    b.classList.toggle('midi-learn-active', active);
    b.textContent = active ? 'MIDI LEARNING' : 'MIDI';
  });
  if (!active) clearMidiLearnTarget();
}

function clearMidiLearnTarget() {
  if (midiLearnPollId) { clearInterval(midiLearnPollId); midiLearnPollId = null; }
  document.querySelectorAll('.slider-col.midi-target').forEach(el => el.classList.remove('midi-target'));
  midiLearningTarget = null;
}

function selectMidiLearnTarget(col) {
  clearMidiLearnTarget();
  midiLearningTarget = {
    fixtureId: col.dataset.fixtureId,
    channelName: col.dataset.channelName,
  };
  col.classList.add('midi-target');
  fetch(`${apiBase}/api/midi/last_event`);
  midiLearnPollId = setInterval(pollMidiLearn, 100);
}

async function pollMidiLearn() {
  if (!midiLearningTarget) return;
  try {
    const res = await fetch(`${apiBase}/api/midi/last_event`);
    const event = await res.json();
    if (event && typeof event.cc === 'number') {
      const { fixtureId, channelName } = midiLearningTarget;
      clearMidiLearnTarget();
      await post(`${apiBase}/api/midi/map`, {
        midi_channel: event.midi_channel,
        cc: event.cc,
        fixture_id: fixtureId,
        channel_name: channelName,
      });
      showToast(`Mapped CC${event.cc} ch${event.midi_channel + 1} → ${fixtureId} / ${channelName}`, 'success');
    }
  } catch (_) {}
}

document.addEventListener('click', e => {
  if (!midiLearning) return;
  const col = e.target.closest('.slider-col');
  if (col && col.dataset.fixtureId && col.dataset.channelName) selectMidiLearnTarget(col);
});

document.querySelectorAll('.midi-learn-btn').forEach(btn => {
  btn.addEventListener('click', () => setMidiLearning(!midiLearning));
});

function zeroAllSliders() {
  document.querySelectorAll('.slider-col input[type=range]').forEach(input => {
    input.value = '0';
    const out = input.parentElement?.querySelector('output');
    if (out) out.textContent = '0';
  });
}

const gmSlider = document.getElementById('grandmaster');
const gmValue = document.getElementById('gm-value');

gmSlider.addEventListener('input', async () => {
  const value = parseInt(gmSlider.value);
  gmValue.textContent = `${value}%`;
  await post(`${apiBase}/api/grandmaster`, { level: value / 100 });
});

const bpmSlider = document.getElementById('fx-bpm');
const bpmValue = document.getElementById('bpm-value');

bpmSlider.addEventListener('input', async () => {
  const value = parseInt(bpmSlider.value);
  bpmValue.textContent = value.toString();
  await post(`${apiBase}/api/fx/bpm`, { bpm: value });
  updateFadeDisplay();
});

const fadeSlider = document.getElementById('fx-fade');
const fadeValue = document.getElementById('fade-value');

function updateFadeDisplay() {
  const percentage = parseInt(fadeSlider.value);
  fadeValue.textContent = `${percentage}%`;
}

fadeSlider.addEventListener('input', async () => {
  updateFadeDisplay();
  const percentage = parseInt(fadeSlider.value);
  await post(`${apiBase}/api/fx/fadetime`, { fade_percentage: percentage / 100.0 });
});

const flashBtn = document.getElementById('flash-btn');
let isFlashing = false;

async function activateFlash() {
  if (!isFlashing) {
    isFlashing = true;
    await post(`${apiBase}/api/flash/on`, {});
  }
}

async function deactivateFlash() {
  if (isFlashing) {
    isFlashing = false;
    await post(`${apiBase}/api/flash/off`, {});
  }
}

flashBtn.addEventListener('mousedown', activateFlash);
flashBtn.addEventListener('mouseup', deactivateFlash);
flashBtn.addEventListener('mouseleave', deactivateFlash);

flashBtn.addEventListener('touchstart', (e) => {
  e.preventDefault();
  activateFlash();
});
flashBtn.addEventListener('touchend', (e) => {
  e.preventDefault();
  deactivateFlash();
});
flashBtn.addEventListener('touchcancel', (e) => {
  e.preventDefault();
  deactivateFlash();
});

let isColorFlashing = false;

async function activateColorFlash(color) {
  if (!isColorFlashing) {
    isColorFlashing = true;
    await post(`${apiBase}/api/flash/color`, color);
  }
}

async function deactivateColorFlash() {
  if (isColorFlashing) {
    isColorFlashing = false;
    await post(`${apiBase}/api/flash/off`, {});
  }
}

function buildColorFlashButtons(colors) {
  const grid = document.getElementById('color-flash-btns');
  if (!grid) return;
  grid.innerHTML = '';

  Object.entries(colors).forEach(([colorName, color]) => {
    const r = Math.min(255, Math.round((color.r + color.w) * 255));
    const g = Math.min(255, Math.round((color.g + color.w) * 255));
    const b = Math.min(255, Math.round((color.b + color.w) * 255));
    const bgColor = `rgb(${r}, ${g}, ${b})`;
    const brightness = r * 0.299 + g * 0.587 + b * 0.114;
    const textColor = brightness > 128 ? '#0b1220' : 'white';

    const btn = document.createElement('button');
    btn.className = 'color-flash-btn';
    btn.style.background = bgColor;
    btn.style.color = textColor;
    if (brightness < 30) btn.style.border = '2px solid #4b5563';
    btn.textContent = colorName.charAt(0).toUpperCase() + colorName.slice(1);

    btn.addEventListener('mousedown', () => activateColorFlash(color));
    btn.addEventListener('mouseup', deactivateColorFlash);
    btn.addEventListener('mouseleave', deactivateColorFlash);
    btn.addEventListener('touchstart', (e) => { e.preventDefault(); activateColorFlash(color); });
    btn.addEventListener('touchend', (e) => { e.preventDefault(); deactivateColorFlash(); });
    btn.addEventListener('touchcancel', (e) => { e.preventDefault(); deactivateColorFlash(); });

    grid.appendChild(btn);
  });
}

const blackoutBtn = document.getElementById('blackout-btn');
let isBlackedOut = false;
let preBlackoutGM = 100;

blackoutBtn.addEventListener('click', async () => {
  if (!isBlackedOut) {
    isBlackedOut = true;
    blackoutBtn.classList.add('active');
    preBlackoutGM = parseInt(gmSlider.value);
    await post(`${apiBase}/api/fx/stop`, {});
    await post(`${apiBase}/api/grandmaster`, { level: 0 });
    gmSlider.value = 0;
    gmValue.textContent = '0%';
  } else {
    isBlackedOut = false;
    blackoutBtn.classList.remove('active');
    await post(`${apiBase}/api/grandmaster`, { level: preBlackoutGM / 100 });
    gmSlider.value = preBlackoutGM;
    gmValue.textContent = `${preBlackoutGM}%`;
  }
});

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const targetTab = tab.dataset.tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`tab-${targetTab}`).classList.add('active');

    if (targetTab === 'colors') {
      loadStaticColors();
      loadColorCycle();
    }
  });
});

async function loadStaticColors() {
  try {
    const res = await fetch(`${apiBase}/api/colors`);
    serverColors = await res.json();
    const grid = document.getElementById('static-colors');

    grid.innerHTML = '';

    Object.keys(serverColors).forEach(colorName => {
      const color = serverColors[colorName];
      const btn = document.createElement('button');
      btn.className = 'color-btn';
      btn.dataset.color = colorName;

      const r = Math.min(255, Math.round((color.r + color.w) * 255));
      const g = Math.min(255, Math.round((color.g + color.w) * 255));
      const b = Math.min(255, Math.round((color.b + color.w) * 255));
      const bgColor = `rgb(${r}, ${g}, ${b})`;

      const brightness = (r * 0.299 + g * 0.587 + b * 0.114);
      const textColor = brightness > 128 ? '#0b1220' : 'white';

      btn.style.background = bgColor;
      btn.style.color = textColor;

      if (brightness < 30) {
        btn.style.border = '2px solid #4b5563';
      }

      btn.textContent = colorName.charAt(0).toUpperCase() + colorName.slice(1);

      btn.draggable = true;
      btn.addEventListener('dragstart', e => {
        e.dataTransfer.effectAllowed = 'copy';
        e.dataTransfer.setData('text/plain', colorName);
      });

      btn.addEventListener('click', async () => {
        await post(`${apiBase}/api/fx/stop`, {});
        document.querySelectorAll('#fx-random-1, #fx-random-2, #fx-random-3, #fx-random-4').forEach(btn => btn.classList.remove('active'));
        await post(`${apiBase}/api/all/color`, color);
        document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });

      grid.appendChild(btn);
    });

    buildColorFlashButtons(serverColors);
  } catch (e) {
    console.error('Failed to load colors:', e);
  }
}

let colorCycle = [];
let serverColors = {};

async function loadColorCycle() {
  try {
    const res = await fetch(`${apiBase}/api/config/color_cycle`);
    const data = await res.json();
    colorCycle = data.color_cycle || [];
    renderColorCycle();
  } catch (e) {
    console.error('Failed to load color cycle:', e);
  }
}

async function saveColorCycle() {
  try {
    await post(`${apiBase}/api/config/color_cycle`, { color_cycle: colorCycle });
  } catch (e) {
    console.error('Failed to save color cycle:', e);
  }
}

function renderColorCycle() {
  const drop = document.getElementById('color-cycle-drop');
  const empty = document.getElementById('color-cycle-empty');
  if (!drop) return;

  drop.querySelectorAll('.cycle-chip').forEach(el => el.remove());

  if (colorCycle.length === 0) {
    if (empty) empty.style.display = '';
  } else {
    if (empty) empty.style.display = 'none';
    colorCycle.forEach((name, idx) => {
      const color = serverColors[name];
      const r = color ? Math.min(255, Math.round((color.r + color.w) * 255)) : 128;
      const g = color ? Math.min(255, Math.round((color.g + color.w) * 255)) : 128;
      const b = color ? Math.min(255, Math.round((color.b + color.w) * 255)) : 128;
      const brightness = r * 0.299 + g * 0.587 + b * 0.114;
      const textColor = brightness > 100 ? '#0b1220' : 'white';

      const chip = document.createElement('div');
      chip.className = 'cycle-chip';
      chip.style.background = `rgb(${r},${g},${b})`;
      chip.style.color = textColor;
      chip.innerHTML = `<span>${name}</span><button class="cycle-chip-remove" style="color:${textColor}" title="Remove">×</button>`;
      chip.querySelector('button').addEventListener('click', () => {
        colorCycle.splice(idx, 1);
        renderColorCycle();
        saveColorCycle();
      });
      drop.appendChild(chip);
    });
  }
}

function initColorCycleDrop() {
  const drop = document.getElementById('color-cycle-drop');
  if (!drop) return;
  drop.addEventListener('dragover', e => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    drop.classList.add('drag-over');
  });
  drop.addEventListener('dragleave', () => drop.classList.remove('drag-over'));
  drop.addEventListener('drop', e => {
    e.preventDefault();
    drop.classList.remove('drag-over');
    const name = e.dataTransfer.getData('text/plain');
    if (name && serverColors[name] !== undefined) {
      colorCycle.push(name);
      renderColorCycle();
      saveColorCycle();
    }
  });
}

document.getElementById('fx-random-1').addEventListener('click', async () => {
  await post(`${apiBase}/api/fx/start`, { fx: 'random_1' });
  document.querySelectorAll('#fx-random-1, #fx-random-2, #fx-random-3, #fx-random-4').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-random-1').classList.add('active');
});

document.getElementById('fx-random-2').addEventListener('click', async () => {
  await post(`${apiBase}/api/fx/start`, { fx: 'random_2' });
  document.querySelectorAll('#fx-random-1, #fx-random-2, #fx-random-3, #fx-random-4').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-random-2').classList.add('active');
});

document.getElementById('fx-random-3').addEventListener('click', async () => {
  await post(`${apiBase}/api/fx/start`, { fx: 'random_3' });
  document.querySelectorAll('#fx-random-1, #fx-random-2, #fx-random-3, #fx-random-4').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-random-3').classList.add('active');
});

document.getElementById('fx-random-4').addEventListener('click', async () => {
  await post(`${apiBase}/api/fx/start`, { fx: 'random_4' });
  document.querySelectorAll('#fx-random-1, #fx-random-2, #fx-random-3, #fx-random-4').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-random-4').classList.add('active');
});

document.getElementById('fx-stop').addEventListener('click', async () => {
  await post(`${apiBase}/api/fx/stop`, {});
  document.querySelectorAll('#fx-random-1, #fx-random-2, #fx-random-3, #fx-random-4').forEach(btn => btn.classList.remove('active'));
});

const xyPad = document.getElementById('xy-pad');
const xyCursor = document.getElementById('xy-cursor');
const xyPanValue = document.getElementById('xy-pan-value');
const xyTiltValue = document.getElementById('xy-tilt-value');

let isDragging = false;

function updateXYPosition(x, y) {
  const rect = xyPad.getBoundingClientRect();
  const pan = Math.max(0, Math.min(1, x / rect.width));
  const tilt = Math.max(0, Math.min(1, 1 - (y / rect.height)));

  xyCursor.style.left = `${pan * 100}%`;
  xyCursor.style.top = `${(1 - tilt) * 100}%`;

  xyPanValue.textContent = pan.toFixed(2);
  xyTiltValue.textContent = tilt.toFixed(2);

  post(`${apiBase}/api/move/center`, { pan, tilt });
}

xyPad?.addEventListener('mousedown', (e) => {
  isDragging = true;
  const rect = xyPad.getBoundingClientRect();
  updateXYPosition(e.clientX - rect.left, e.clientY - rect.top);
});

xyPad?.addEventListener('touchstart', (e) => {
  isDragging = true;
  const rect = xyPad.getBoundingClientRect();
  const touch = e.touches[0];
  updateXYPosition(touch.clientX - rect.left, touch.clientY - rect.top);
  e.preventDefault();
});

document.addEventListener('mousemove', (e) => {
  if (isDragging && xyPad) {
    const rect = xyPad.getBoundingClientRect();
    updateXYPosition(e.clientX - rect.left, e.clientY - rect.top);
  }
});

document.addEventListener('touchmove', (e) => {
  if (isDragging && xyPad) {
    const rect = xyPad.getBoundingClientRect();
    const touch = e.touches[0];
    updateXYPosition(touch.clientX - rect.left, touch.clientY - rect.top);
    e.preventDefault();
  }
});

document.addEventListener('mouseup', () => { isDragging = false; });
document.addEventListener('touchend', () => { isDragging = false; });

document.getElementById('xy-center')?.addEventListener('click', () => {
  updateXYPosition(xyPad.offsetWidth / 2, xyPad.offsetHeight / 2);
});

const fxSizeSlider = document.getElementById('fx-size-slider');
const fxSizeValue = document.getElementById('fx-size-value');

fxSizeSlider?.addEventListener('input', async (e) => {
  const sizePercent = parseInt(e.target.value);
  const size = sizePercent / 100;
  fxSizeValue.textContent = sizePercent;
  await post(`${apiBase}/api/move/fx_size`, { size });
});

const movePhaseSlider = document.getElementById('move-phase-slider');
const movePhaseValue = document.getElementById('move-phase-value');

movePhaseSlider?.addEventListener('input', async (e) => {
  const phasePercent = parseInt(e.target.value);
  const phase = phasePercent / 100;
  movePhaseValue.textContent = phasePercent;
  await post(`${apiBase}/api/move/phase`, { phase });
});

const moveSpeedSlider = document.getElementById('move-speed-slider');
const moveSpeedValue = document.getElementById('move-speed-value');

moveSpeedSlider?.addEventListener('input', async (e) => {
  const speedPercent = parseInt(e.target.value);
  moveSpeedValue.textContent = speedPercent;

  let multiplier;
  if (speedPercent === 50) {
    multiplier = 1.0;
  } else if (speedPercent < 50) {
    multiplier = speedPercent / 50;
  } else {
    multiplier = 1.0 + ((speedPercent - 50) / 50);
  }

  await post(`${apiBase}/api/move/speed`, { multiplier });
});

document.getElementById('fx-pan-sway')?.addEventListener('click', async () => {
  await post(`${apiBase}/api/move/fx`, { fx: 'pan_sway' });
  document.querySelectorAll('#fx-pan-sway, #fx-tilt-sway, #fx-circle, #fx-eight, #fx-lissajous, #fx-diamond').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-pan-sway').classList.add('active');
});

document.getElementById('fx-tilt-sway')?.addEventListener('click', async () => {
  await post(`${apiBase}/api/move/fx`, { fx: 'tilt_sway' });
  document.querySelectorAll('#fx-pan-sway, #fx-tilt-sway, #fx-circle, #fx-eight, #fx-lissajous, #fx-diamond').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-tilt-sway').classList.add('active');
});

document.getElementById('fx-circle')?.addEventListener('click', async () => {
  await post(`${apiBase}/api/move/fx`, { fx: 'circle' });
  document.querySelectorAll('#fx-pan-sway, #fx-tilt-sway, #fx-circle, #fx-eight, #fx-lissajous, #fx-diamond').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-circle').classList.add('active');
});

document.getElementById('fx-eight')?.addEventListener('click', async () => {
  await post(`${apiBase}/api/move/fx`, { fx: 'eight' });
  document.querySelectorAll('#fx-pan-sway, #fx-tilt-sway, #fx-circle, #fx-eight, #fx-lissajous, #fx-diamond').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-eight').classList.add('active');
});

document.getElementById('fx-lissajous')?.addEventListener('click', async () => {
  await post(`${apiBase}/api/move/fx`, { fx: 'lissajous' });
  document.querySelectorAll('#fx-pan-sway, #fx-tilt-sway, #fx-circle, #fx-eight, #fx-lissajous, #fx-diamond').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-lissajous').classList.add('active');
});

document.getElementById('fx-diamond')?.addEventListener('click', async () => {
  await post(`${apiBase}/api/move/fx`, { fx: 'diamond' });
  document.querySelectorAll('#fx-pan-sway, #fx-tilt-sway, #fx-circle, #fx-eight, #fx-lissajous, #fx-diamond').forEach(btn => btn.classList.remove('active'));
  document.getElementById('fx-diamond').classList.add('active');
});

document.getElementById('fx-move-off')?.addEventListener('click', async () => {
  await post(`${apiBase}/api/move/fx`, { fx: 'off' });
  document.querySelectorAll('#fx-pan-sway, #fx-tilt-sway, #fx-circle, #fx-eight, #fx-lissajous, #fx-diamond').forEach(btn => btn.classList.remove('active'));
});

async function updateActiveColor() {
  try {
    const res = await fetch(`${apiBase}/api/fx/status`);
    const status = await res.json();

    if (status.current_colors && status.current_colors.length > 0) {
      document.querySelectorAll('.color-btn').forEach(btn => {
        btn.classList.toggle('active', status.current_colors.includes(btn.dataset.color));
      });
    }

    const activeFx = status.running ? status.current_fx : null;
    document.querySelectorAll('#fx-random-1, #fx-random-2, #fx-random-3, #fx-random-4').forEach(btn => {
      const fxName = btn.id.replace('fx-', '').replace(/-/g, '_');
      btn.classList.toggle('active', fxName === activeFx);
    });

    if (status.fade_percentage !== undefined) {
      const fadeSlider = document.getElementById('fx-fade');
      const fadeValue = document.getElementById('fade-value');
      if (fadeSlider) {
        const percentage = Math.round(status.fade_percentage * 100);
        if (parseInt(fadeSlider.value) !== percentage) {
          fadeSlider.value = percentage;
          fadeValue.textContent = `${percentage}%`;
        }
      }
    }
  } catch (e) {}
}

async function updateLiveValues() {
  try {
    const [statesRes, gmRes, bpmRes] = await Promise.all([
      getStates(),
      fetch(`${apiBase}/api/grandmaster`).then(r => r.json()),
      fetch(`${apiBase}/api/fx/bpm`).then(r => r.json()),
    ]);

    document.querySelectorAll('.slider-col').forEach(col => {
      const fixtureId = col.dataset.fixtureId;
      const channelName = col.dataset.channelName;
      const input = col.querySelector('input[type=range]');
      const output = col.querySelector('output');
      if (!input || !output || input.matches(':active')) return;

      if (fixtureId === '_global') {
        if (channelName === 'grandmaster') {
          const level = Math.round(gmRes.level * 100);
          if (parseInt(input.value) !== level) {
            input.value = level;
            output.textContent = `${level}%`;
          }
        } else if (channelName === 'bpm') {
          const bpm = bpmRes.bpm;
          if (parseInt(input.value) !== bpm) {
            input.value = bpm;
            output.textContent = bpm.toString();
          }
        }
      } else if (statesRes[fixtureId] && statesRes[fixtureId][channelName] !== undefined) {
        const dmxValue = Math.round(statesRes[fixtureId][channelName] * 255);
        if (parseInt(input.value) !== dmxValue) {
          input.value = dmxValue;
          output.textContent = dmxValue.toString();
        }
      }
    });
  } catch (e) {}
}

loadFixtures();
loadStaticColors().then(() => loadColorCycle());
initColorCycleDrop();

async function loadGrandmaster() {
  try {
    const res = await fetch(`${apiBase}/api/grandmaster`);
    const data = await res.json();
    const level = Math.round(data.level * 100);
    gmSlider.value = level;
    gmValue.textContent = `${level}%`;
  } catch (e) {
    console.error('Failed to load grandmaster:', e);
  }
}

async function loadBPM() {
  try {
    const res = await fetch(`${apiBase}/api/fx/bpm`);
    const data = await res.json();
    const bpm = data.bpm;
    bpmSlider.value = bpm;
    bpmValue.textContent = bpm.toString();
  } catch (e) {
    console.error('Failed to load BPM:', e);
  }
}

async function loadMoveState() {
  try {
    const res = await fetch(`${apiBase}/api/move/state`);
    const data = await res.json();

    if (xyPad && xyCursor && xyPanValue && xyTiltValue) {
      const pan = data.center_pan;
      const tilt = data.center_tilt;

      xyCursor.style.left = `${pan * 100}%`;
      xyCursor.style.top = `${(1 - tilt) * 100}%`;
      xyPanValue.textContent = pan.toFixed(2);
      xyTiltValue.textContent = tilt.toFixed(2);
    }

    if (fxSizeSlider && fxSizeValue) {
      const sizePercent = Math.round(data.fx_size * 100);
      fxSizeSlider.value = sizePercent;
      fxSizeValue.textContent = sizePercent;
    }

    if (movePhaseSlider && movePhaseValue) {
      const phasePercent = Math.round(data.move_phase * 100);
      movePhaseSlider.value = phasePercent;
      movePhaseValue.textContent = phasePercent;
    }

    if (moveSpeedSlider && moveSpeedValue) {
      const multiplier = data.move_speed_multiplier || 1.0;
      let speedPercent;

      if (multiplier === 1.0) {
        speedPercent = 50;
      } else if (multiplier < 1.0) {
        speedPercent = Math.round(multiplier * 50);
      } else {
        speedPercent = Math.round(50 + ((multiplier - 1.0) * 50));
      }

      moveSpeedSlider.value = speedPercent;
      moveSpeedValue.textContent = speedPercent;
    }
  } catch (e) {
    console.error('Failed to load move state:', e);
  }
}

loadGrandmaster();
loadBPM();
loadMoveState();
setInterval(updateLiveValues, 500);
setInterval(updateActiveColor, 500);

// ── Scenes ────────────────────────────────────────────────────────
let scenes = [];
let activeSceneId = null;
let deleteSceneId = null;

async function loadScenes() {
  try {
    const res = await fetch(`${apiBase}/api/scenes`);
    const data = await res.json();
    scenes = data.scenes || [];
    renderScenes();
  } catch (e) {
    console.error('Failed to load scenes:', e);
  }
}

function renderScenes() {
  const grid = document.getElementById('scenes-grid');
  const empty = document.getElementById('scenes-empty');
  if (!grid) return;

  grid.querySelectorAll('.scene-btn').forEach(el => el.remove());

  if (scenes.length === 0) {
    if (empty) empty.style.display = '';
    return;
  }
  if (empty) empty.style.display = 'none';

  scenes.forEach(scene => {
    const btn = document.createElement('button');
    btn.className = 'scene-btn' + (scene.id === activeSceneId ? ' active' : '');
    btn.dataset.sceneId = scene.id;

    const fixtureCount = Object.keys(scene.fixtures || {}).length;
    const parts = [];
    if (fixtureCount > 0) parts.push(`${fixtureCount} fix`);
    if (scene.color_fx) parts.push('color fx');
    if (scene.move_fx) parts.push('move fx');
    if (scene.color_cycle) parts.push('cycle');
    if (scene.grandmaster !== null && scene.grandmaster !== undefined) parts.push('gm');

    btn.innerHTML = `
      <span class="scene-btn__name">${scene.name}</span>
      <span class="scene-btn__meta">${parts.join(' / ') || 'empty'}</span>
      <span class="scene-btn__actions">
        <button class="scene-btn__action scene-action-delete" title="Delete">&times;</button>
      </span>
    `;

    btn.addEventListener('click', async (e) => {
      if (e.target.closest('.scene-btn__action')) return;
      activeSceneId = scene.id;
      await post(`${apiBase}/api/scenes/${scene.id}/activate`);
      renderScenes();
    });

    btn.querySelector('.scene-action-delete').addEventListener('click', (e) => {
      e.stopPropagation();
      deleteSceneId = scene.id;
      document.getElementById('scene-delete-msg').textContent = `Delete scene "${scene.name}"?`;
      document.getElementById('scene-delete-modal').style.display = 'flex';
    });

    grid.appendChild(btn);
  });
}

// Save scene modal
document.getElementById('scene-save-btn')?.addEventListener('click', async () => {
  // Populate fixture checkboxes
  const container = document.getElementById('scene-fixture-checkboxes');
  container.innerHTML = '';
  try {
    const res = await fetch(`${apiBase}/api/fixtures`);
    const data = await res.json();
    (data.fixtures || []).forEach(fx => {
      const label = document.createElement('label');
      label.className = 'check-row';
      label.innerHTML = `<input type="checkbox" class="form-checkbox scene-fixture-cb" value="${fx.id}" checked> ${fx.id} <span class="pill">${fx.type}</span>`;
      container.appendChild(label);
    });
  } catch (e) {}

  document.getElementById('scene-name-input').value = '';
  document.getElementById('scene-inc-color-cycle').checked = false;
  document.getElementById('scene-inc-color-fx').checked = false;
  document.getElementById('scene-inc-move-fx').checked = false;
  document.getElementById('scene-inc-grandmaster').checked = false;
  document.getElementById('scene-save-modal').style.display = 'flex';
  document.getElementById('scene-name-input').focus();
});

document.getElementById('scene-save-confirm')?.addEventListener('click', async () => {
  const name = document.getElementById('scene-name-input').value.trim();
  if (!name) {
    showToast('Scene name is required', 'warning');
    return;
  }

  const fixtureIds = Array.from(document.querySelectorAll('.scene-fixture-cb:checked')).map(cb => cb.value);

  await post(`${apiBase}/api/scenes`, {
    name,
    fixture_ids: fixtureIds,
    include_color_cycle: document.getElementById('scene-inc-color-cycle').checked,
    include_color_fx: document.getElementById('scene-inc-color-fx').checked,
    include_move_fx: document.getElementById('scene-inc-move-fx').checked,
    include_grandmaster: document.getElementById('scene-inc-grandmaster').checked,
  });

  document.getElementById('scene-save-modal').style.display = 'none';
  showToast(`Scene "${name}" saved`, 'success');
  loadScenes();
});

document.getElementById('scene-save-cancel')?.addEventListener('click', () => {
  document.getElementById('scene-save-modal').style.display = 'none';
});

// Delete scene modal
document.getElementById('scene-delete-confirm')?.addEventListener('click', async () => {
  if (deleteSceneId) {
    await post(`${apiBase}/api/scenes/${deleteSceneId}/delete`);
    if (activeSceneId === deleteSceneId) activeSceneId = null;
    deleteSceneId = null;
  }
  document.getElementById('scene-delete-modal').style.display = 'none';
  loadScenes();
});

document.getElementById('scene-delete-cancel')?.addEventListener('click', () => {
  deleteSceneId = null;
  document.getElementById('scene-delete-modal').style.display = 'none';
});

loadScenes();
