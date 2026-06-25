// Fixture Library Editor Logic
let fixtureLibrary = null;       // full fixtures.json content
let fxEditorChannels = [];       // channel rows being edited in modal
let fxEditorCwMapping = {};      // color wheel mapping being edited
let fxEditorCwOpen = false;
let fxEditorListenersInit = false;

const FX_CHANNEL_TYPES = [
  'color', 'dimmer', 'pan', 'tilt', 'pan_fine', 'tilt_fine',
  'shutter', 'speed', 'other',
];

const FX_CH_COLORS = {
  dimmer: '#f59e0b', color: '#38bdf8',
  pan: '#a78bfa', tilt: '#a78bfa',
  pan_fine: '#7c3aed', tilt_fine: '#7c3aed',
  shutter: '#94a3b8', speed: '#34d399', other: '#6b7280',
};

// ─── Data ────────────────────────────────────────────────────────────────────

async function loadFixtureLibrary() {
  try {
    const res = await fetch(`${apiBase}/api/config/fixtures`);
    fixtureLibrary = await res.json();
    renderFixtureTypes();
  } catch (e) {
    console.error('Failed to load fixture library:', e);
    showToast('Failed to load fixture library', 'error');
  }
}

async function saveFixtureLibrary() {
  try {
    const res = await post(`${apiBase}/api/config/fixtures`, fixtureLibrary);
    if (res && res.success) {
      showToast('Fixture library saved!', 'success');
    } else {
      showToast('Saved. Restart to apply to active fixtures.', 'warning');
    }
  } catch (e) {
    console.error('Failed to save fixture library:', e);
    showToast('Failed to save: ' + e.message, 'error');
  }
}

// ─── Rendering ───────────────────────────────────────────────────────────────

function channelTypeSummary(channels) {
  const counts = {};
  channels.forEach(ch => { counts[ch.type] = (counts[ch.type] || 0) + 1; });
  return Object.entries(counts)
    .map(([t, n]) => {
      const col = FX_CH_COLORS[t] || '#6b7280';
      return `<span class="ch-badge" style="background:${col}22;border:1px solid ${col}55;">${n}× ${t}</span>`;
    })
    .join(' ');
}

function renderFixtureTypes() {
  const container = document.getElementById('fixture-types-list');
  const summary   = document.getElementById('fixture-lib-summary');
  if (!container) return;
  container.innerHTML = '';

  const entries = Object.entries(fixtureLibrary || {});
  if (summary) summary.textContent = `${entries.length} fixture type${entries.length !== 1 ? 's' : ''} defined`;

  if (entries.length === 0) {
    container.innerHTML = '<div style="color:#6b7280;font-size:14px;padding:20px 0;">No fixture types defined yet. Click "+ Add Fixture Type" to create one.</div>';
    return;
  }

  entries.forEach(([key, def]) => {
    const channels = def.channels || [];
    const hasCw    = def.color_wheel_mapping && Object.keys(def.color_wheel_mapping).length > 0;
    const isMoving = channels.some(ch => ch.type === 'pan');
    const accent   = isMoving ? '#7c3aed' : '#1e40af';

    const row = document.createElement('div');
    row.className = 'list-card list-card--row';
    row.style.borderLeft = `3px solid ${accent}`;
    row.innerHTML = `
      <div class="list-card__body">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:5px;">
          <span style="font-weight:600;font-size:14px;">${def.name}</span>
          <code style="font-size:11px;padding:2px 7px;background:#0f172a;border:1px solid var(--border);border-radius:4px;color:var(--muted);">${key}</code>
          ${def.manufacturer ? `<span class="list-card__meta" style="font-size:12px;">${def.manufacturer}</span>` : ''}
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:5px;align-items:center;">
          ${channelTypeSummary(channels)}
          ${hasCw ? '<span class="ch-badge" style="background:#7c3aed22;border:1px solid #7c3aed55;">colour wheel</span>' : ''}
          ${def.dimmer_on_black ? '<span class="ch-badge" style="background:#f59e0b22;border:1px solid #f59e0b55;">dimmer on black</span>' : ''}
        </div>
      </div>
      <div class="list-card__actions">
        <button class="secondary btn-sm" onclick="editFixtureType('${key}')">Edit</button>
        <button class="btn--delete btn-sm" onclick="deleteFixtureType('${key}')">Delete</button>
      </div>
    `;
    container.appendChild(row);
  });
}

// ─── Modal: channel list ──────────────────────────────────────────────────────

function renderModalChannels() {
  const list    = document.getElementById('ftm-channels-list');
  const empty   = document.getElementById('ftm-channels-empty');
  if (!list) return;
  list.innerHTML = '';

  if (fxEditorChannels.length === 0) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';

  fxEditorChannels.forEach((ch, i) => {
    const row = document.createElement('div');
    row.className = 'ch-row';
    row.innerHTML = `
      <div class="ch-row__num">ch${i + 1}</div>
      <input type="text" value="${ch.name}" placeholder="channel name"
        class="form-input" onchange="fxChSetName(${i}, this.value)">
      <select class="form-input" onchange="fxChSetType(${i}, this.value)">
        ${FX_CHANNEL_TYPES.map(t =>
          `<option value="${t}" ${ch.type === t ? 'selected' : ''}>${t}</option>`
        ).join('')}
      </select>
      <button class="btn--delete" style="padding:5px;width:36px;" onclick="fxChRemove(${i})">✕</button>
    `;
    list.appendChild(row);
  });
}

window.fxChSetName = function(i, val) { fxEditorChannels[i].name = val.trim(); };
window.fxChSetType = function(i, val) { fxEditorChannels[i].type = val; };
window.fxChRemove  = function(i) {
  fxEditorChannels.splice(i, 1);
  renderModalChannels();
};

// ─── Modal: colour wheel mapping ─────────────────────────────────────────────

const CW_PRESET_COLORS = ['white', 'red', 'green', 'blue', 'yellow', 'orange', 'cyan', 'magenta'];

function renderCwMapping() {
  const list = document.getElementById('ftm-cw-list');
  if (!list) return;
  list.innerHTML = '';

  Object.entries(fxEditorCwMapping).forEach(([colorName, dmxVal]) => {
    const row = document.createElement('div');
    row.className = 'cw-row';
    row.innerHTML = `
      <input type="text" value="${colorName}" placeholder="colour name"
        class="form-input" data-cw-key="${colorName}" onchange="fxCwRenameKey('${colorName}', this.value)">
      <input type="number" value="${dmxVal}" min="0" max="255" placeholder="DMX"
        class="form-input" onchange="fxCwSetVal('${colorName}', parseInt(this.value))">
      <button class="btn--delete" style="padding:5px;width:36px;" onclick="fxCwRemove('${colorName}')">✕</button>
    `;
    list.appendChild(row);
  });
}

window.fxCwRenameKey = function(oldKey, newKey) {
  newKey = newKey.trim();
  if (!newKey || newKey === oldKey) return;
  const val = fxEditorCwMapping[oldKey];
  delete fxEditorCwMapping[oldKey];
  fxEditorCwMapping[newKey] = val;
  renderCwMapping();
};
window.fxCwSetVal = function(key, val) { fxEditorCwMapping[key] = isNaN(val) ? 0 : Math.max(0, Math.min(255, val)); };
window.fxCwRemove = function(key) { delete fxEditorCwMapping[key]; renderCwMapping(); };

function addCwEntry() {
  // Pick next unused preset name, otherwise "colour"
  const existing = Object.keys(fxEditorCwMapping);
  const next = CW_PRESET_COLORS.find(c => !existing.includes(c)) || `colour${existing.length + 1}`;
  fxEditorCwMapping[next] = 0;
  renderCwMapping();
}

// ─── Modal: open / close ─────────────────────────────────────────────────────

function openFixtureTypeModal(typeKey) {
  const isEdit = Boolean(typeKey);
  document.getElementById('fixture-type-modal-title').textContent = isEdit ? 'Edit Fixture Type' : 'Add Fixture Type';
  document.getElementById('ftm-original-key').value = typeKey || '';

  const def = isEdit ? fixtureLibrary[typeKey] : null;

  document.getElementById('ftm-key').value          = typeKey || '';
  document.getElementById('ftm-key').disabled       = isEdit;
  document.getElementById('ftm-name').value         = def ? def.name : '';
  document.getElementById('ftm-manufacturer').value = def ? (def.manufacturer || '') : '';
  document.getElementById('ftm-dimmer-on-black').checked = def ? Boolean(def.dimmer_on_black) : false;

  // Channels
  fxEditorChannels = def
    ? def.channels.map(ch => ({ name: ch.name, type: ch.type }))
    : [];
  renderModalChannels();

  // Colour wheel mapping
  fxEditorCwMapping = def && def.color_wheel_mapping
    ? { ...def.color_wheel_mapping }
    : {};
  fxEditorCwOpen = Object.keys(fxEditorCwMapping).length > 0;
  const cwSection = document.getElementById('ftm-cw-section');
  const cwToggle  = document.getElementById('ftm-cw-toggle');
  cwSection.style.display = fxEditorCwOpen ? 'block' : 'none';
  cwToggle.textContent    = `${fxEditorCwOpen ? '▼' : '▶'} Color Wheel Mapping`;
  renderCwMapping();

  // Clear errors
  ['ftm-key-error', 'ftm-name-error'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
  });

  document.getElementById('fixture-type-modal').style.display = 'flex';
}

window.editFixtureType = function(typeKey) { openFixtureTypeModal(typeKey); };

window.deleteFixtureType = function(typeKey) {
  const def = fixtureLibrary[typeKey];
  const name = def ? def.name : typeKey;

  // Check if used in patch (patchConfig comes from patch_logic.js scope)
  let usedIn = [];
  if (typeof patchConfig !== 'undefined' && patchConfig) {
    Object.entries(patchConfig.universes || {}).forEach(([uid, udata]) => {
      (udata.fixtures || []).forEach(f => {
        if (f.type === typeKey) usedIn.push(`${f.id} (U${uid})`);
      });
    });
  }

  let msg = `Delete fixture type "${name}" (${typeKey})?`;
  if (usedIn.length) msg += `\n\nWarning: still used in patch by: ${usedIn.join(', ')}`;

  if (!confirm(msg)) return;
  delete fixtureLibrary[typeKey];
  saveFixtureLibrary();
  renderFixtureTypes();
};

// ─── Validation ──────────────────────────────────────────────────────────────

function validateFixtureTypeModal(originalKey) {
  let ok = true;

  const key    = document.getElementById('ftm-key').value.trim();
  const name   = document.getElementById('ftm-name').value.trim();
  const keyErr = document.getElementById('ftm-key-error');
  const nmErr  = document.getElementById('ftm-name-error');
  keyErr.style.display = 'none';
  nmErr.style.display  = 'none';

  if (!key) {
    keyErr.textContent = 'Type key is required'; keyErr.style.display = 'block'; ok = false;
  } else if (!/^[a-z0-9_]+$/.test(key)) {
    keyErr.textContent = 'Only lowercase letters, numbers, and underscores'; keyErr.style.display = 'block'; ok = false;
  } else if (!originalKey && fixtureLibrary[key]) {
    keyErr.textContent = `Key "${key}" already exists`; keyErr.style.display = 'block'; ok = false;
  }

  if (!name) {
    nmErr.textContent = 'Display name is required'; nmErr.style.display = 'block'; ok = false;
  }

  if (fxEditorChannels.length === 0) {
    showToast('Add at least one channel', 'warning'); ok = false;
  }

  // Check all channel names are filled
  const unnamed = fxEditorChannels.filter(ch => !ch.name);
  if (unnamed.length) {
    showToast(`${unnamed.length} channel(s) have no name`, 'warning'); ok = false;
  }

  return ok;
}

// ─── Event wiring ────────────────────────────────────────────────────────────

function initFixtureEditorListeners() {
  if (fxEditorListenersInit) return;
  fxEditorListenersInit = true;

  document.getElementById('add-fixture-type-btn')?.addEventListener('click', () => openFixtureTypeModal(null));

  document.getElementById('ftm-add-channel-btn')?.addEventListener('click', () => {
    fxEditorChannels.push({ name: '', type: 'other' });
    renderModalChannels();
  });

  document.getElementById('ftm-cw-toggle')?.addEventListener('click', () => {
    fxEditorCwOpen = !fxEditorCwOpen;
    document.getElementById('ftm-cw-section').style.display = fxEditorCwOpen ? 'block' : 'none';
    document.getElementById('ftm-cw-toggle').textContent =
      `${fxEditorCwOpen ? '▼' : '▶'} Color Wheel Mapping`;
  });

  document.getElementById('ftm-add-cw-btn')?.addEventListener('click', addCwEntry);

  document.getElementById('ftm-save-btn')?.addEventListener('click', () => {
    const originalKey = document.getElementById('ftm-original-key').value;
    if (!validateFixtureTypeModal(originalKey)) return;

    const key          = originalKey || document.getElementById('ftm-key').value.trim();
    const name         = document.getElementById('ftm-name').value.trim();
    const manufacturer = document.getElementById('ftm-manufacturer').value.trim();
    const dimmerOnBlack = document.getElementById('ftm-dimmer-on-black').checked;

    const channels = fxEditorChannels.map((ch, i) => ({
      index: i,
      name:  ch.name,
      type:  ch.type,
      range: [0, 255],
    }));

    const def = { name, channels };
    if (manufacturer)  def.manufacturer       = manufacturer;
    if (dimmerOnBlack) def.dimmer_on_black     = true;
    const cwKeys = Object.keys(fxEditorCwMapping);
    if (cwKeys.length) def.color_wheel_mapping = { ...fxEditorCwMapping };

    fixtureLibrary[key] = def;

    document.getElementById('fixture-type-modal').style.display = 'none';
    saveFixtureLibrary();
    renderFixtureTypes();
  });

  document.getElementById('ftm-cancel-btn')?.addEventListener('click', () => {
    document.getElementById('fixture-type-modal').style.display = 'none';
  });

  // Load when tab is activated
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.dataset.tab === 'fixtures') loadFixtureLibrary();
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initFixtureEditorListeners);
} else {
  initFixtureEditorListeners();
}
