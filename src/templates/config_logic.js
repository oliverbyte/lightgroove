// Config Tab Logic
let artnetConfig = null;
let colorsConfig = null;

async function loadArtNetConfig() {
  try {
    const res = await fetch(`${apiBase}/api/config/artnet`);
    artnetConfig = await res.json();
    renderNodes();
    renderMappings();
    renderGlobalSettings();
  } catch (e) {
    console.error('Failed to load ArtNet config:', e);
  }
}

async function loadColorsConfig() {
  try {
    const res = await fetch(`${apiBase}/api/config/colors`);
    colorsConfig = await res.json();
    renderColors();
  } catch (e) {
    console.error('Failed to load colors config:', e);
  }
}

async function saveArtNetConfig() {
  try {
    const response = await post(`${apiBase}/api/config/artnet`, artnetConfig);
    if (response && response.reloaded) {
      showToast('Configuration saved and reloaded successfully!', 'success');
    } else {
      showToast('Configuration saved! Restart the application for changes to take effect.', 'warning');
    }
  } catch (e) {
    console.error('Failed to save ArtNet config:', e);
    showToast('Failed to save configuration: ' + e.message, 'error');
  }
}

async function saveColorsConfig() {
  try {
    const response = await post(`${apiBase}/api/config/colors`, colorsConfig);
    showToast('Colors saved successfully!', 'success');
  } catch (e) {
    console.error('Failed to save colors config:', e);
    showToast('Failed to save colors: ' + e.message, 'error');
  }
}

function renderNodes() {
  const nodesList = document.getElementById('nodes-list');
  if (!nodesList) return;
  nodesList.innerHTML = artnetConfig.nodes.length
    ? '<div class="subsection-label" style="margin-top: 12px;">Configured Nodes</div>'
    : '';

  artnetConfig.nodes.forEach(node => {
    const nodeCard = document.createElement('div');
    nodeCard.className = 'list-card';
    nodeCard.innerHTML = `
      <div class="list-card__row">
        <div class="list-card__body">
          <div class="list-card__name">${node.name}</div>
          <div class="list-card__meta">
            <div>ID: ${node.id}</div>
            <div>IP: ${node.ip}</div>
            <div>Universes: ${node.universes.join(', ')}</div>
            ${node.description ? `<div style="margin-top: 5px;">${node.description}</div>` : ''}
            <div class="badge-row">
              <span class="badge ${node.enabled ? 'badge--success' : 'badge--danger'}">${node.enabled ? 'Enabled' : 'Disabled'}</span>
              <span class="badge ${node.protocol === 'sacn' ? 'badge--purple' : 'badge--info'}">${node.protocol === 'sacn' ? 'sACN' : 'ArtNet'}</span>
              ${node.broadcast ? `<span class="badge badge--neutral">${node.protocol === 'sacn' ? 'Multicast' : 'Broadcast'}</span>` : ''}
            </div>
          </div>
        </div>
        <div class="list-card__actions">
          <button class="secondary btn-sm" onclick="editNode('${node.id}')">Edit</button>
          <button class="btn--delete btn-sm" onclick="deleteNode('${node.id}')">Delete</button>
        </div>
      </div>
    `;
    nodesList.appendChild(nodeCard);
  });
}

function renderMappings() {
  const mappingsList = document.getElementById('mappings-list');
  if (!mappingsList) return;
  mappingsList.innerHTML = '';

  Object.entries(artnetConfig.universe_mapping).forEach(([dmxUniverse, mapping]) => {
    const mappingCard = document.createElement('div');
    mappingCard.className = 'list-card';
    mappingCard.innerHTML = `
      <div class="list-card__row">
        <div class="list-card__body">
          <div class="list-card__name">DMX Universe ${dmxUniverse}</div>
          <div class="list-card__meta">
            <div>Node: ${mapping.node_id}</div>
            <div>ArtNet Universe: ${mapping.artnet_universe}</div>
            <div class="badge-row">
              <span class="badge ${mapping.output_mode === 'artnet' ? 'badge--info' : mapping.output_mode === 'sacn' ? 'badge--purple' : 'badge--neutral'}">${mapping.output_mode === 'sacn' ? 'sACN' : mapping.output_mode}</span>
            </div>
          </div>
        </div>
        <div class="list-card__actions">
          <button class="secondary btn-sm" onclick="editMapping('${dmxUniverse}')">Edit</button>
          <button class="btn--delete btn-sm" onclick="deleteMapping('${dmxUniverse}')">Delete</button>
        </div>
      </div>
    `;
    mappingsList.appendChild(mappingCard);
  });
}

function renderGlobalSettings() {
  const defaultMode = document.getElementById('default-output-mode');
  const fps = document.getElementById('fps');
  if (defaultMode) defaultMode.value = artnetConfig.default_output_mode;
  if (fps) fps.value = artnetConfig.fps;
}

// Node CRUD
function updateNodeBroadcastLabel() {
  const proto = document.getElementById('node-protocol').value;
  document.getElementById('node-broadcast-label').textContent =
    proto === 'sacn' ? 'Multicast Mode' : 'Broadcast Mode';
}

function updateMappingUniverseLabel() {
  const mode = document.getElementById('mapping-output-mode').value;
  document.getElementById('mapping-universe-label').textContent =
    mode === 'sacn' ? 'sACN Universe (1-63999)' : 'ArtNet Universe';
}

window.editNode = function(nodeId) {
  const node = artnetConfig.nodes.find(n => n.id === nodeId);
  if (!node) return;

  document.getElementById('node-modal-title').textContent = 'Edit Node';
  document.getElementById('node-modal-id').value = nodeId;
  document.getElementById('node-id').value = node.id;
  document.getElementById('node-id').disabled = true;
  document.getElementById('node-protocol').value = node.protocol || 'artnet';
  document.getElementById('node-name').value = node.name;
  document.getElementById('node-ip').value = node.ip;
  document.getElementById('node-universes').value = node.universes.join(', ');
  document.getElementById('node-description').value = node.description || '';
  document.getElementById('node-broadcast').checked = node.broadcast;
  document.getElementById('node-enabled').checked = node.enabled;
  updateNodeBroadcastLabel();

  document.getElementById('node-modal').style.display = 'flex';
};

window.deleteNode = function(nodeId) {
  if (confirm('Delete node "' + nodeId + '"? This will also remove any universe mappings using this node.')) {
    artnetConfig.nodes = artnetConfig.nodes.filter(n => n.id !== nodeId);
    Object.keys(artnetConfig.universe_mapping).forEach(universe => {
      if (artnetConfig.universe_mapping[universe].node_id === nodeId) {
        delete artnetConfig.universe_mapping[universe];
      }
    });
    saveArtNetConfig();
    renderNodes();
    renderMappings();
  }
};

// Mapping CRUD
window.editMapping = function(dmxUniverse) {
  const mapping = artnetConfig.universe_mapping[dmxUniverse];
  if (!mapping) return;
  
  document.getElementById('mapping-modal-title').textContent = 'Edit Universe Mapping';
  document.getElementById('mapping-modal-universe').value = dmxUniverse;
  document.getElementById('mapping-universe').value = dmxUniverse;
  document.getElementById('mapping-universe').disabled = true;
  document.getElementById('mapping-artnet-universe').value = mapping.artnet_universe;
  document.getElementById('mapping-output-mode').value = mapping.output_mode;
  updateMappingUniverseLabel();
  
  updateNodeOptions();
  // Set node value AFTER updating options so the option exists
  document.getElementById('mapping-node').value = mapping.node_id;
  document.getElementById('mapping-modal').style.display = 'flex';
};

window.deleteMapping = function(dmxUniverse) {
  if (confirm('Delete mapping for DMX Universe ' + dmxUniverse + '?')) {
    delete artnetConfig.universe_mapping[dmxUniverse];
    saveArtNetConfig();
    renderMappings();
  }
};

function updateNodeOptions() {
  const select = document.getElementById('mapping-node');
  select.innerHTML = '<option value="">Select a node...</option>';
  artnetConfig.nodes.forEach(node => {
    const option = document.createElement('option');
    option.value = node.id;
    option.textContent = node.name + ' (' + node.id + ')';
    select.appendChild(option);
  });
}

// Color rendering and CRUD
function renderColors() {
  const container = document.getElementById('colors-list');
  if (!container || !colorsConfig) return;

  container.innerHTML = '';
  const colors = colorsConfig.colors || {};

  Object.keys(colors).forEach(colorName => {
    const color = colors[colorName];
    const colorCard = document.createElement('div');
    colorCard.className = 'list-card';

    const r = Math.round(color.r * 255);
    const g = Math.round(color.g * 255);
    const b = Math.round(color.b * 255);
    const rgbColor = `rgb(${r}, ${g}, ${b})`;

    colorCard.innerHTML = `
      <div class="list-card__row list-card--row">
        <div class="list-card__body">
          <div class="list-card__name">${colorName}</div>
          <div class="list-card__meta">R: ${color.r.toFixed(2)}, G: ${color.g.toFixed(2)}, B: ${color.b.toFixed(2)}, W: ${color.w.toFixed(2)}</div>
        </div>
        <div class="list-card__actions">
          <div class="color-swatch" style="background: ${rgbColor};"></div>
          <button class="secondary btn-sm" onclick="editColor('${colorName}')">Edit</button>
          <button class="btn--delete btn-sm" onclick="deleteColor('${colorName}')">Delete</button>
        </div>
      </div>
    `;
    container.appendChild(colorCard);
  });
}

window.editColor = function(colorName) {
  const color = colorsConfig.colors[colorName];
  if (!color) return;
  
  document.getElementById('color-modal-title').textContent = 'Edit Color';
  document.getElementById('color-modal-id').value = colorName;
  document.getElementById('color-name').value = colorName;
  document.getElementById('color-name').disabled = true;
  document.getElementById('color-r').value = color.r;
  document.getElementById('color-g').value = color.g;
  document.getElementById('color-b').value = color.b;
  document.getElementById('color-w').value = color.w;
  updateColorPreview();
  
  document.getElementById('color-modal').style.display = 'flex';
};

window.deleteColor = function(colorName) {
  if (confirm('Delete color "' + colorName + '"?')) {
    delete colorsConfig.colors[colorName];
    saveColorsConfig();
    renderColors();
  }
};

function updateColorPreview() {
  const r = parseFloat(document.getElementById('color-r').value) || 0;
  const g = parseFloat(document.getElementById('color-g').value) || 0;
  const b = parseFloat(document.getElementById('color-b').value) || 0;
  const w = parseFloat(document.getElementById('color-w').value) || 0;
  
  // Clamp values between 0 and 1
  const rClamped = Math.max(0, Math.min(1, r));
  const gClamped = Math.max(0, Math.min(1, g));
  const bClamped = Math.max(0, Math.min(1, b));
  const wClamped = Math.max(0, Math.min(1, w));
  
  // Convert to 0-255 range and add white channel contribution
  const rInt = Math.round((rClamped + wClamped) * 255);
  const gInt = Math.round((gClamped + wClamped) * 255);
  const bInt = Math.round((bClamped + wClamped) * 255);
  
  // Clamp final values to 255
  const rFinal = Math.min(255, rInt);
  const gFinal = Math.min(255, gInt);
  const bFinal = Math.min(255, bInt);
  
  const preview = document.getElementById('color-preview');
  if (preview) {
    preview.style.background = `rgb(${rFinal}, ${gFinal}, ${bFinal})`;
  }
}

// ArtNet Network Discovery
async function scanForNodes() {
  const btn = document.getElementById('scan-network-btn');
  const status = document.getElementById('discovery-status');
  const list = document.getElementById('discovered-nodes-list');

  btn.disabled = true;
  btn.textContent = 'Scanning...';
  status.style.display = 'block';
  status.textContent = 'Scanning network for ArtNet nodes (2 seconds)...';
  list.innerHTML = '';

  try {
    const res = await fetch(`${apiBase}/api/artnet/discover`);
    const data = await res.json();

    btn.disabled = false;
    btn.textContent = 'Scan Network';

    if (data.error) {
      status.textContent = 'Scan failed: ' + data.error;
      return;
    }

    if (data.nodes && data.nodes.length > 0) {
      status.textContent = `Found ${data.nodes.length} node(s) on the network.`;
      renderDiscoveredNodes(data.nodes);
    } else {
      status.textContent = 'No ArtNet nodes found on the network.';
    }
  } catch (e) {
    btn.disabled = false;
    btn.textContent = 'Scan Network';
    status.textContent = 'Scan failed: ' + e.message;
  }
}

function renderDiscoveredNodes(nodes) {
  const list = document.getElementById('discovered-nodes-list');
  list.innerHTML = '<div class="subsection-label">Discovered on Network</div>';

  nodes.forEach(node => {
    const alreadyAdded = artnetConfig && artnetConfig.nodes.some(n => n.ip === node.ip);
    const card = document.createElement('div');
    card.className = 'list-card';

    const universesText = node.universes && node.universes.length
      ? node.universes.join(', ')
      : '—';

    const addBtn = alreadyAdded
      ? '<span class="badge badge--success" style="font-size: 12px; padding: 4px 10px; border-radius: 4px;">Added</span>'
      : `<button class="secondary btn-sm" onclick='addDiscoveredNode(${JSON.stringify(node)})'>Add</button>`;

    card.innerHTML = `
      <div class="list-card__row">
        <div class="list-card__body">
          <div class="list-card__name">${node.name || node.ip}</div>
          <div class="list-card__meta">
            <div>IP: ${node.ip}</div>
            ${node.short_name && node.short_name !== node.name ? `<div>Short name: ${node.short_name}</div>` : ''}
            <div>Ports: ${node.num_ports} &nbsp;&bull;&nbsp; Universes: ${universesText}</div>
          </div>
        </div>
        <div class="list-card__actions">${addBtn}</div>
      </div>
    `;
    list.appendChild(card);
  });
}

window.addDiscoveredNode = function(node) {
  document.getElementById('node-modal-title').textContent = 'Add Discovered Node';
  document.getElementById('node-modal-id').value = '';
  document.getElementById('node-id').value = node.ip.replace(/\./g, '-');
  document.getElementById('node-id').disabled = false;
  document.getElementById('node-protocol').value = 'artnet';
  document.getElementById('node-name').value = node.name || node.ip;
  document.getElementById('node-ip').value = node.ip;
  document.getElementById('node-universes').value = node.universes && node.universes.length
    ? node.universes.join(', ')
    : '0';
  document.getElementById('node-description').value = node.long_name || '';
  document.getElementById('node-broadcast').checked = false;
  document.getElementById('node-enabled').checked = true;
  updateNodeBroadcastLabel();

  document.getElementById('node-modal').style.display = 'flex';
};

// MIDI Paired Devices
async function loadPairedDevices() {
  try {
    const res = await fetch(`${apiBase}/api/midi/paired`);
    const data = await res.json();
    renderPairedDevices(data);
  } catch (e) {
    console.error('Failed to load paired MIDI devices:', e);
  }
}

function renderPairedDevices(data) {
  const list = document.getElementById('midi-paired-list');
  if (!list) return;
  const all = [
    ...data.inputs.map(d => ({ ...d, direction: 'input' })),
    ...data.outputs.map(d => ({ ...d, direction: 'output' })),
  ];
  if (all.length === 0) {
    list.innerHTML = '<div class="summary-text">No paired devices.</div>';
    return;
  }
  list.innerHTML = '';
  all.forEach(({ name, connected, direction }) => {
    const dir = direction === 'input' ? 'IN' : 'OUT';
    const row = document.createElement('div');
    row.className = 'list-card list-card--row';
    row.innerHTML = `
      <div class="list-card__body">
        <div class="list-card__title">${name}</div>
        <div class="badge-row">
          <span class="badge ${dir === 'IN' ? 'badge--info' : 'badge--purple'}">${dir}</span>
          <span class="badge ${connected ? 'badge--success' : 'badge--neutral'}">${connected ? 'Connected' : 'Not connected'}</span>
        </div>
      </div>
      <button class="btn--delete btn-sm" style="flex-shrink: 0;"
        data-paired-name="${name}" data-paired-dir="${direction}">Delete</button>
    `;
    row.querySelector('button').addEventListener('click', deletePairing);
    list.appendChild(row);
  });
}

async function deletePairing(e) {
  const btn = e.currentTarget;
  const name = btn.dataset.pairedName;
  const direction = btn.dataset.pairedDir;
  if (!confirm(`Delete pairing for "${name}"?\n\nThis will disconnect the device and clear all learned MIDI mappings.`)) return;
  btn.disabled = true;
  try {
    await post(`${apiBase}/api/midi/delete_pairing`, { name, direction });
    showToast(`Pairing deleted and MIDI mappings cleared.`, 'success');
    loadPairedDevices();
    // Refresh scan list active state if visible
    midiActiveConfig = { active_inputs: [], active_outputs: [] };
    renderMidiDevices();
  } catch (err) {
    showToast('Failed to delete pairing: ' + err.message, 'error');
    btn.disabled = false;
  }
}

// MIDI Device Discovery
let midiActiveConfig = { active_inputs: [], active_outputs: [] };
let midiDiscoveredDevices = { inputs: [], outputs: [] };

async function scanMidiDevices() {
  const btn = document.getElementById('scan-midi-btn');
  const status = document.getElementById('midi-status');

  btn.disabled = true;
  btn.textContent = 'Scanning...';
  status.style.display = 'block';
  status.textContent = 'Scanning for MIDI devices...';

  try {
    const [devRes, cfgRes] = await Promise.all([
      fetch(`${apiBase}/api/midi/devices`),
      fetch(`${apiBase}/api/midi/config`),
    ]);
    const devData = await devRes.json();
    const cfgData = cfgRes.ok ? await cfgRes.json() : { active_inputs: [], active_outputs: [] };

    btn.disabled = false;
    btn.textContent = 'Scan MIDI Devices';

    if (devData.error) {
      status.textContent = 'Scan failed: ' + devData.error;
      return;
    }

    midiDiscoveredDevices = devData;
    midiActiveConfig = cfgData;

    const total = devData.inputs.length + devData.outputs.length;
    status.textContent = total ? `Found ${total} MIDI port(s).` : 'No MIDI devices found.';
    renderMidiDevices();
  } catch (e) {
    btn.disabled = false;
    btn.textContent = 'Scan MIDI Devices';
    status.textContent = 'Scan failed: ' + e.message;
  }
}

function renderMidiDevices() {
  const list = document.getElementById('midi-devices-list');
  list.innerHTML = '';

  const makeRow = (name, direction) => {
    const dir = direction === 'input' ? 'IN' : 'OUT';
    const isActive = direction === 'input'
      ? midiActiveConfig.active_inputs.includes(name)
      : midiActiveConfig.active_outputs.includes(name);

    const row = document.createElement('div');
    row.className = 'list-card list-card--row';

    const activeBadge = isActive
      ? '<span class="badge badge--success" style="margin-left: 8px;">Active</span>'
      : '';

    row.innerHTML = `
      <div class="list-card__body">
        <div class="list-card__title">${name}${activeBadge}</div>
      </div>
      <div class="list-card__actions">
        <span class="badge ${dir === 'IN' ? 'badge--info' : 'badge--purple'}">${dir}</span>
        <button class="secondary btn-sm" data-midi-name="${name}" data-midi-dir="${direction}" data-midi-active="${isActive}">
          ${isActive ? 'Deactivate' : 'Activate'}
        </button>
      </div>
    `;

    row.querySelector('button').addEventListener('click', toggleMidiDevice);
    return row;
  };

  midiDiscoveredDevices.inputs.forEach(name => list.appendChild(makeRow(name, 'input')));
  midiDiscoveredDevices.outputs.forEach(name => list.appendChild(makeRow(name, 'output')));
}

async function toggleMidiDevice(e) {
  const btn = e.currentTarget;
  const name = btn.dataset.midiName;
  const direction = btn.dataset.midiDir;
  const isActive = btn.dataset.midiActive === 'true';
  const endpoint = isActive ? '/api/midi/deactivate' : '/api/midi/activate';

  btn.disabled = true;
  try {
    const res = await post(`${apiBase}${endpoint}`, { name, direction });
    if (res) {
      midiActiveConfig = res;
      renderMidiDevices();
      loadPairedDevices();
    }
  } catch (e) {
    showToast('MIDI toggle failed: ' + e.message, 'error');
  } finally {
    btn.disabled = false;
  }
}

// Event listeners
let eventListenersInitialized = false;

function initConfigEventListeners() {
  // Prevent duplicate event listener bindings
  if (eventListenersInitialized) return;
  eventListenersInitialized = true;
  
  const scanBtn = document.getElementById('scan-network-btn');
  if (scanBtn) {
    scanBtn.addEventListener('click', scanForNodes);
  }

  const scanMidiBtn = document.getElementById('scan-midi-btn');
  if (scanMidiBtn) {
    scanMidiBtn.addEventListener('click', scanMidiDevices);
  }

  const addNodeBtn = document.getElementById('add-node-btn');
  if (addNodeBtn) {
    addNodeBtn.addEventListener('click', () => {
      document.getElementById('node-modal-title').textContent = 'Add Node';
      document.getElementById('node-modal-id').value = '';
      document.getElementById('node-id').value = '';
      document.getElementById('node-id').disabled = false;
      document.getElementById('node-protocol').value = 'artnet';
      document.getElementById('node-name').value = '';
      document.getElementById('node-ip').value = '';
      document.getElementById('node-universes').value = '';
      document.getElementById('node-description').value = '';
      document.getElementById('node-broadcast').checked = false;
      document.getElementById('node-enabled').checked = true;
      updateNodeBroadcastLabel();

      document.getElementById('node-modal').style.display = 'flex';
    });
  }

  const nodeProtocolSel = document.getElementById('node-protocol');
  if (nodeProtocolSel) {
    nodeProtocolSel.addEventListener('change', updateNodeBroadcastLabel);
  }

  const nodeSaveBtn = document.getElementById('node-modal-save');
  if (nodeSaveBtn) {
    nodeSaveBtn.addEventListener('click', () => {
      const isEdit = document.getElementById('node-modal-id').value !== '';
      const nodeId = document.getElementById('node-id').value.trim();
      
      if (!nodeId) {
        showToast('Node ID is required', 'warning');
        return;
      }
      
      const node = {
        id: nodeId,
        protocol: document.getElementById('node-protocol').value,
        name: document.getElementById('node-name').value.trim() || nodeId,
        ip: document.getElementById('node-ip').value.trim(),
        universes: document.getElementById('node-universes').value.split(',').map(u => parseInt(u.trim())).filter(u => !isNaN(u)),
        broadcast: document.getElementById('node-broadcast').checked,
        enabled: document.getElementById('node-enabled').checked,
        description: document.getElementById('node-description').value.trim()
      };
      
      if (isEdit) {
        const index = artnetConfig.nodes.findIndex(n => n.id === document.getElementById('node-modal-id').value);
        if (index !== -1) {
          artnetConfig.nodes[index] = node;
        }
      } else {
        if (artnetConfig.nodes.some(n => n.id === nodeId)) {
          showToast('Node ID already exists', 'warning');
          return;
        }
        artnetConfig.nodes.push(node);
      }
      
      document.getElementById('node-modal').style.display = 'none';
      saveArtNetConfig();
      renderNodes();
    });
  }

  const nodeCancelBtn = document.getElementById('node-modal-cancel');
  if (nodeCancelBtn) {
    nodeCancelBtn.addEventListener('click', () => {
      document.getElementById('node-modal').style.display = 'none';
    });
  }

  const addMappingBtn = document.getElementById('add-mapping-btn');
  if (addMappingBtn) {
    addMappingBtn.addEventListener('click', () => {
      document.getElementById('mapping-modal-title').textContent = 'Add Universe Mapping';
      document.getElementById('mapping-modal-universe').value = '';
      document.getElementById('mapping-universe').value = '';
      document.getElementById('mapping-universe').disabled = false;
      document.getElementById('mapping-node').value = '';
      document.getElementById('mapping-artnet-universe').value = '0';
      document.getElementById('mapping-output-mode').value = 'artnet';
      
      updateNodeOptions();
      updateMappingUniverseLabel();
      document.getElementById('mapping-modal').style.display = 'flex';
    });
  }

  const mappingOutputMode = document.getElementById('mapping-output-mode');
  if (mappingOutputMode) {
    mappingOutputMode.addEventListener('change', updateMappingUniverseLabel);
  }

  const mappingSaveBtn = document.getElementById('mapping-modal-save');
  if (mappingSaveBtn) {
    mappingSaveBtn.addEventListener('click', () => {
      const isEdit = document.getElementById('mapping-modal-universe').value !== '';
      const dmxUniverse = document.getElementById('mapping-universe').value.trim();
      
      if (!dmxUniverse) {
        showToast('DMX Universe is required', 'warning');
        return;
      }
      
      const nodeId = document.getElementById('mapping-node').value;
      if (!nodeId) {
        showToast('Please select a node', 'warning');
        return;
      }
      
      const mapping = {
        node_id: nodeId,
        artnet_universe: parseInt(document.getElementById('mapping-artnet-universe').value) || 0,
        output_mode: document.getElementById('mapping-output-mode').value
      };
      
      if (!isEdit && artnetConfig.universe_mapping[dmxUniverse]) {
        showToast('Mapping for this DMX Universe already exists', 'warning');
        return;
      }
      
      artnetConfig.universe_mapping[dmxUniverse] = mapping;
      
      document.getElementById('mapping-modal').style.display = 'none';
      saveArtNetConfig();
      renderMappings();
    });
  }

  const mappingCancelBtn = document.getElementById('mapping-modal-cancel');
  if (mappingCancelBtn) {
    mappingCancelBtn.addEventListener('click', () => {
      document.getElementById('mapping-modal').style.display = 'none';
    });
  }

  const addColorBtn = document.getElementById('add-color-btn');
  if (addColorBtn) {
    addColorBtn.addEventListener('click', () => {
      document.getElementById('color-modal-title').textContent = 'Add Color';
      document.getElementById('color-modal-id').value = '';
      document.getElementById('color-name').value = '';
      document.getElementById('color-name').disabled = false;
      document.getElementById('color-r').value = '0';
      document.getElementById('color-g').value = '0';
      document.getElementById('color-b').value = '0';
      document.getElementById('color-w').value = '0';
      updateColorPreview();
      
      document.getElementById('color-modal').style.display = 'flex';
    });
  }

  const colorSaveBtn = document.getElementById('color-modal-save');
  if (colorSaveBtn) {
    colorSaveBtn.addEventListener('click', () => {
      const isEdit = document.getElementById('color-modal-id').value !== '';
      const colorName = document.getElementById('color-name').value.trim();
      
      if (!colorName) {
        showToast('Please enter a color name', 'error');
        return;
      }
      
      const color = {
        r: parseFloat(document.getElementById('color-r').value) || 0,
        g: parseFloat(document.getElementById('color-g').value) || 0,
        b: parseFloat(document.getElementById('color-b').value) || 0,
        w: parseFloat(document.getElementById('color-w').value) || 0
      };
      
      if (!isEdit && colorsConfig.colors[colorName]) {
        showToast('Color name already exists', 'error');
        return;
      }
      
      colorsConfig.colors[colorName] = color;
      saveColorsConfig();
      renderColors();
      document.getElementById('color-modal').style.display = 'none';
    });
  }

  const colorCancelBtn = document.getElementById('color-modal-cancel');
  if (colorCancelBtn) {
    colorCancelBtn.addEventListener('click', () => {
      document.getElementById('color-modal').style.display = 'none';
    });
  }

  // Color preview update on input change
  ['color-r', 'color-g', 'color-b', 'color-w'].forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener('input', updateColorPreview);
      input.addEventListener('change', updateColorPreview);
    }
  });

  const saveGlobalBtn = document.getElementById('save-global-settings-btn');
  if (saveGlobalBtn) {
    saveGlobalBtn.addEventListener('click', () => {
      artnetConfig.default_output_mode = document.getElementById('default-output-mode').value;
      artnetConfig.fps = parseInt(document.getElementById('fps').value) || 44;
      saveArtNetConfig();
    });
  }

  const restartBtn = document.getElementById('restart-btn');
  if (restartBtn) {
    restartBtn.addEventListener('click', async () => {
      if (!confirm('Restart LightGroove?\n\nThe server will be unavailable for a few seconds.')) return;
      restartBtn.disabled = true;
      restartBtn.textContent = 'Restarting…';
      try {
        await fetch(`${apiBase}/api/restart`, { method: 'POST' });
      } catch (_) {
        // Expected — connection drops as the process restarts
      }
      showToast('LightGroove is restarting…', 'info', 8000);
      // Connection monitor will detect the drop and reconnect automatically.
      // Re-enable the button once the server is back.
      const poll = setInterval(async () => {
        try {
          const r = await fetch(`${apiBase}/api/grandmaster`);
          if (r.ok) {
            clearInterval(poll);
            restartBtn.disabled = false;
            restartBtn.textContent = 'Restart LightGroove';
            showToast('LightGroove is back online', 'success');
          }
        } catch (_) {}
      }, 1000);
    });
  }

  // Load config when Config tab is activated
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.dataset.tab === 'config') {
        if (!artnetConfig) {
          loadArtNetConfig();
          initConfigEventListeners();
        }
        // Always reload colors to pick up manual changes
        loadColorsConfig();
        loadPairedDevices();
      }
    });
  });

  // Load paired devices on initial page load
  loadPairedDevices();
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initConfigEventListeners);
} else {
  initConfigEventListeners();
}
