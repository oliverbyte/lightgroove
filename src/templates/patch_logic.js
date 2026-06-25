// Patch Editor Logic
let patchConfig = null;
let fixtureTypes = null;

async function loadPatchData() {
  try {
    const [patchRes, typesRes] = await Promise.all([
      fetch(`${apiBase}/api/config/patch`),
      fetch(`${apiBase}/api/config/fixtures`)
    ]);
    patchConfig = await patchRes.json();
    fixtureTypes = await typesRes.json();
    renderPatch();
    populateFixtureTypeSelect();
  } catch (e) {
    console.error('Failed to load patch data:', e);
    showToast('Failed to load patch data', 'error');
  }
}

async function savePatchData() {
  try {
    const response = await post(`${apiBase}/api/config/patch`, patchConfig);
    if (response && response.reloaded) {
      showToast('Patch saved — fixtures reloaded!', 'success');
    } else {
      showToast('Patch saved. Restart to apply changes.', 'warning');
    }
  } catch (e) {
    console.error('Failed to save patch:', e);
    showToast('Failed to save patch: ' + e.message, 'error');
  }
}

// --- Helpers ---

function channelCount(typeKey) {
  return (fixtureTypes && fixtureTypes[typeKey])
    ? fixtureTypes[typeKey].channels.length
    : 0;
}

function endAddress(startAddr, typeKey) {
  const n = channelCount(typeKey);
  return n ? startAddr + n - 1 : startAddr;
}

function isMovingHead(typeKey) {
  if (!fixtureTypes || !fixtureTypes[typeKey]) return false;
  return fixtureTypes[typeKey].channels.some(ch => ch.type === 'pan');
}

function allPatchedFixtures() {
  const out = [];
  Object.entries(patchConfig.universes || {}).forEach(([uid, udata]) => {
    (udata.fixtures || []).forEach(f => out.push({ universeId: uid, fixture: f }));
  });
  return out;
}

function findOverlaps(fixtures) {
  const bad = new Set();
  for (let i = 0; i < fixtures.length; i++) {
    const a = fixtures[i];
    const aEnd = endAddress(a.start_address, a.type);
    for (let j = i + 1; j < fixtures.length; j++) {
      const b = fixtures[j];
      const bEnd = endAddress(b.start_address, b.type);
      if (a.start_address <= bEnd && b.start_address <= aEnd) {
        bad.add(a.id);
        bad.add(b.id);
      }
    }
  }
  return bad;
}

// --- Rendering ---

function renderPatch() {
  const container = document.getElementById('patch-universes');
  const summaryEl  = document.getElementById('patch-summary');
  if (!container) return;

  container.innerHTML = '';
  const universes = patchConfig.universes || {};
  const universeKeys = Object.keys(universes).sort((a, b) => parseInt(a) - parseInt(b));
  let totalFixtures = 0;

  if (universeKeys.length === 0) {
    container.innerHTML = '<div class="empty-msg">No fixtures patched yet. Click "+ Add Fixture" to get started.</div>';
    if (summaryEl) summaryEl.textContent = '0 fixtures';
    return;
  }

  universeKeys.forEach(uid => {
    const udata    = universes[uid];
    const fixtures = udata.fixtures || [];
    totalFixtures += fixtures.length;
    const overlaps = findOverlaps(fixtures);

    const section = document.createElement('div');
    section.className = 'universe-section';

    const overlapBanner = overlaps.size > 0
      ? '<div class="overlap-banner">⚠ DMX address overlap detected — highlighted fixtures share channels</div>'
      : '';

    section.innerHTML = `
      <div class="universe-header">
        <h3 class="universe-header__title">Universe ${uid}</h3>
        <span class="universe-header__count">${fixtures.length} fixture${fixtures.length !== 1 ? 's' : ''}</span>
      </div>
      ${overlapBanner}
      <div id="u${uid}-list"></div>
    `;
    container.appendChild(section);

    const list = section.querySelector(`#u${uid}-list`);
    fixtures.forEach((fx, idx) => {
      const eAddr    = endAddress(fx.start_address, fx.type);
      const typeDef  = fixtureTypes && fixtureTypes[fx.type];
      const typeName = typeDef ? typeDef.name : fx.type;
      const hasOvlp  = overlaps.has(fx.id);
      const accent   = isMovingHead(fx.type) ? '#7c3aed' : '#1e40af';

      const row = document.createElement('div');
      row.className = `list-card list-card--row${hasOvlp ? ' list-card--overlap' : ''}`;
      row.style.borderLeft = `3px solid ${accent}`;
      row.draggable = true;
      row.dataset.universeId = uid;
      row.dataset.fixtureIdx = idx;

      row.innerHTML = `
        <span class="drag-handle" title="Drag to reorder">⠿</span>
        <div class="list-card__body">
          <div style="display:flex;align-items:center;gap:7px;flex-wrap:wrap;">
            <span style="font-weight:600;font-size:14px;">${fx.id}</span>
            <span class="ch-badge" style="background:${accent}22;border:1px solid ${accent}55;">${typeName}</span>
            <span class="ch-badge" style="background:#1f2937;border:1px solid #374151;color:#9ca3af;">ch ${fx.start_address}–${eAddr}</span>
            ${typeDef ? `<span class="ch-badge" style="background:#1f2937;border:1px solid #374151;color:#9ca3af;">${typeDef.channels.length} ch</span>` : ''}
          </div>
          ${fx.description ? `<div class="list-card__meta" style="margin-top:3px;">${fx.description}</div>` : ''}
        </div>
        <div class="list-card__actions">
          <button class="secondary btn-sm" onclick="editFixture('${uid}','${fx.id}')">Edit</button>
          <button class="btn--delete btn-sm" onclick="deleteFixture('${uid}','${fx.id}')">Delete</button>
        </div>
      `;

      // Drag events for reordering
      row.addEventListener('dragstart', (e) => {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', `${uid}:${idx}`);
        row.classList.add('dragging');
      });
      row.addEventListener('dragend', () => {
        row.classList.remove('dragging');
        list.querySelectorAll('.list-card').forEach(el => {
          el.classList.remove('drag-over-above', 'drag-over-below');
        });
      });
      row.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        const rect = row.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        list.querySelectorAll('.list-card').forEach(el => {
          el.classList.remove('drag-over-above', 'drag-over-below');
        });
        if (e.clientY < midY) {
          row.classList.add('drag-over-above');
        } else {
          row.classList.add('drag-over-below');
        }
      });
      row.addEventListener('dragleave', () => {
        row.classList.remove('drag-over-above', 'drag-over-below');
      });
      row.addEventListener('drop', (e) => {
        e.preventDefault();
        row.classList.remove('drag-over-above', 'drag-over-below');
        const data = e.dataTransfer.getData('text/plain');
        const [srcUid, srcIdxStr] = data.split(':');
        const srcIdx = parseInt(srcIdxStr);
        if (srcUid !== uid) return; // Only reorder within same universe
        const targetIdx = parseInt(row.dataset.fixtureIdx);
        if (srcIdx === targetIdx) return;

        const rect = row.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        let insertIdx = e.clientY < midY ? targetIdx : targetIdx + 1;

        const uFixtures = patchConfig.universes[uid].fixtures;
        const [moved] = uFixtures.splice(srcIdx, 1);
        if (insertIdx > srcIdx) insertIdx--;
        uFixtures.splice(insertIdx, 0, moved);

        savePatchData();
        renderPatch();
      });

      list.appendChild(row);
    });
  });

  if (summaryEl) {
    summaryEl.textContent = `${totalFixtures} fixture${totalFixtures !== 1 ? 's' : ''} across ${universeKeys.length} universe${universeKeys.length !== 1 ? 's' : ''}`;
  }
}

function populateFixtureTypeSelect() {
  const select = document.getElementById('fixture-type');
  if (!select || !fixtureTypes) return;
  const current = select.value;
  select.innerHTML = '<option value="">Select fixture type...</option>';
  Object.entries(fixtureTypes).forEach(([key, def]) => {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = `${def.name}  (${def.channels.length} ch)`;
    select.appendChild(opt);
  });
  if (current) select.value = current;
}

// --- Modal helpers ---

const CH_COLORS = {
  dimmer: '#f59e0b', color: '#38bdf8',
  pan: '#a78bfa', tilt: '#a78bfa',
  pan_fine: '#7c3aed', tilt_fine: '#7c3aed',
  shutter: '#94a3b8', speed: '#34d399', other: '#6b7280',
};

function updateChannelPreview() {
  const typeKey = document.getElementById('fixture-type').value;
  const preview = document.getElementById('channel-preview');
  const list    = document.getElementById('channel-preview-list');
  if (!typeKey || !fixtureTypes || !fixtureTypes[typeKey]) {
    preview.style.display = 'none';
    return;
  }
  list.innerHTML = '';
  fixtureTypes[typeKey].channels.forEach(ch => {
    const col  = CH_COLORS[ch.type] || '#6b7280';
    const pill = document.createElement('span');
    pill.className = 'ch-pill';
    pill.style.border = `1px solid ${col}55`;
    pill.style.background = `${col}22`;
    pill.textContent = `${ch.index + 1}: ${ch.name}`;
    list.appendChild(pill);
  });
  preview.style.display = 'block';
  refreshEndAddress();
}

function refreshEndAddress() {
  const typeKey  = document.getElementById('fixture-type').value;
  const startVal = parseInt(document.getElementById('fixture-start-address').value) || 0;
  const el       = document.getElementById('fixture-end-address');
  if (!typeKey || !startVal) { el.textContent = '—'; el.style.color = '#9ca3af'; return; }
  const eAddr = endAddress(startVal, typeKey);
  if (eAddr > 512) {
    el.textContent = `${eAddr} — exceeds 512!`;
    el.style.color = '#ef4444';
  } else {
    el.textContent = eAddr;
    el.style.color = '#9ca3af';
  }
}

function clearModalErrors() {
  document.getElementById('fixture-id-error').style.display   = 'none';
  document.getElementById('fixture-addr-error').style.display = 'none';
}

function validateModal(originalId) {
  clearModalErrors();
  const id        = document.getElementById('fixture-id').value.trim();
  const typeKey   = document.getElementById('fixture-type').value;
  const universeN = document.getElementById('fixture-universe').value;
  const startAddr = parseInt(document.getElementById('fixture-start-address').value);
  const idErr     = document.getElementById('fixture-id-error');
  const addrErr   = document.getElementById('fixture-addr-error');
  let ok = true;

  if (!id)       { idErr.textContent = 'Fixture ID is required';          idErr.style.display = 'block';   ok = false; }
  if (!typeKey)  { showToast('Please select a fixture type', 'warning');   ok = false; }
  if (!universeN){ showToast('Please enter a universe number', 'warning'); ok = false; }
  if (!startAddr || startAddr < 1 || startAddr > 512) {
    addrErr.textContent = 'Start address must be between 1 and 512';
    addrErr.style.display = 'block';
    ok = false;
  }
  if (!ok) return false;

  // ID uniqueness
  const conflict = allPatchedFixtures().find(({ fixture }) => fixture.id === id && id !== originalId);
  if (conflict) {
    idErr.textContent = `ID "${id}" is already used in Universe ${conflict.universeId}`;
    idErr.style.display = 'block';
    return false;
  }

  // Address range fits in universe
  const eAddr = endAddress(startAddr, typeKey);
  if (eAddr > 512) {
    addrErr.textContent = `End address ${eAddr} exceeds the 512-channel universe limit`;
    addrErr.style.display = 'block';
    return false;
  }

  // Overlap check within target universe
  const udata = patchConfig.universes[universeN] || { fixtures: [] };
  const ov = (udata.fixtures || []).find(f => {
    if (f.id === originalId) return false;
    const fEnd = endAddress(f.start_address, f.type);
    return startAddr <= fEnd && f.start_address <= eAddr;
  });
  if (ov) {
    addrErr.textContent = `Overlaps with "${ov.id}" (ch ${ov.start_address}–${endAddress(ov.start_address, ov.type)})`;
    addrErr.style.display = 'block';
    return false;
  }

  return true;
}

function openModalForAdd() {
  document.getElementById('fixture-modal-title').textContent = 'Add Fixture';
  document.getElementById('fixture-modal-original-id').value = '';
  document.getElementById('fixture-id').value = '';
  document.getElementById('fixture-universe').value = '1';
  document.getElementById('fixture-type').value = '';
  document.getElementById('fixture-start-address').value = '';
  document.getElementById('fixture-description').value = '';
  document.getElementById('fixture-end-address').textContent = '—';
  document.getElementById('fixture-end-address').style.color = '#9ca3af';
  document.getElementById('channel-preview').style.display = 'none';
  clearModalErrors();
  document.getElementById('fixture-modal').style.display = 'flex';
}

window.editFixture = function(universeId, fixtureId) {
  const fx = (patchConfig.universes[universeId]?.fixtures || []).find(f => f.id === fixtureId);
  if (!fx) return;
  document.getElementById('fixture-modal-title').textContent = 'Edit Fixture';
  document.getElementById('fixture-modal-original-id').value = fixtureId;
  document.getElementById('fixture-id').value = fx.id;
  document.getElementById('fixture-universe').value = universeId;
  document.getElementById('fixture-type').value = fx.type;
  document.getElementById('fixture-start-address').value = fx.start_address;
  document.getElementById('fixture-description').value = fx.description || '';
  clearModalErrors();
  updateChannelPreview();
  document.getElementById('fixture-modal').style.display = 'flex';
};

window.deleteFixture = function(universeId, fixtureId) {
  if (!confirm(`Delete fixture "${fixtureId}" from Universe ${universeId}?`)) return;
  const udata = patchConfig.universes[universeId];
  if (!udata) return;
  udata.fixtures = udata.fixtures.filter(f => f.id !== fixtureId);
  if (udata.fixtures.length === 0) delete patchConfig.universes[universeId];
  savePatchData();
  renderPatch();
};

// --- Event wiring ---

let patchListenersInit = false;

function initPatchEventListeners() {
  if (patchListenersInit) return;
  patchListenersInit = true;

  document.getElementById('add-fixture-btn')?.addEventListener('click', openModalForAdd);

  document.getElementById('fixture-type')?.addEventListener('change', updateChannelPreview);
  document.getElementById('fixture-start-address')?.addEventListener('input', refreshEndAddress);

  document.getElementById('fixture-modal-save')?.addEventListener('click', () => {
    const originalId = document.getElementById('fixture-modal-original-id').value;
    if (!validateModal(originalId)) return;

    const id        = document.getElementById('fixture-id').value.trim();
    const universeId = document.getElementById('fixture-universe').value;
    const typeKey   = document.getElementById('fixture-type').value;
    const startAddr = parseInt(document.getElementById('fixture-start-address').value);
    const desc      = document.getElementById('fixture-description').value.trim();

    const fixture = { id, type: typeKey, start_address: startAddr };
    if (desc) fixture.description = desc;

    // Remove from old location when editing (handles universe change)
    if (originalId) {
      Object.values(patchConfig.universes).forEach(udata => {
        udata.fixtures = udata.fixtures.filter(f => f.id !== originalId);
      });
      // Prune universes that are now empty (except the destination)
      Object.keys(patchConfig.universes).forEach(uid => {
        if (uid !== universeId && patchConfig.universes[uid].fixtures.length === 0) {
          delete patchConfig.universes[uid];
        }
      });
    }

    if (!patchConfig.universes[universeId]) {
      patchConfig.universes[universeId] = { fixtures: [] };
    }
    patchConfig.universes[universeId].fixtures.push(fixture);

    document.getElementById('fixture-modal').style.display = 'none';
    savePatchData();
    renderPatch();
  });

  document.getElementById('fixture-modal-cancel')?.addEventListener('click', () => {
    document.getElementById('fixture-modal').style.display = 'none';
  });

  // Load when the Patch tab is activated
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.dataset.tab === 'patch') loadPatchData();
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPatchEventListeners);
} else {
  initPatchEventListeners();
}
