// Config Tab Logic
let artnetConfig = null;
let colorsConfig = null;
let patchConfig = null;
let fixtureTypes = null;

async function loadFixtureTypes() {
  try {
    const res = await fetch(`${apiBase}/api/config/fixtures`);
    fixtureTypes = await res.json();
  } catch (e) {
    console.error('Failed to load fixture types:', e);
  }
}

async function loadPatchConfig() {
  try {
    const res = await fetch(`${apiBase}/api/config/patch`);
    patchConfig = await res.json();
    renderPatches();
  } catch (e) {
    console.error('Failed to load patch config:', e);
  }
}

async function savePatchConfig() {
  try {
    const response = await post(`${apiBase}/api/config/patch`, patchConfig);
    if (response && response.reloaded) {
      showToast('Patch configuration saved and reloaded successfully!', 'success');
      // Reload faders to reflect changes
      if (typeof loadFaders === 'function') {
        await loadFaders();
      }
    } else {
      showToast('Patch configuration saved!', 'success');
    }
  } catch (e) {
    console.error('Failed to save patch config:', e);
    showToast('Failed to save patch configuration: ' + e.message, 'error');
  }
}

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

function renderPatches() {
  const patchesList = document.getElementById('patches-list');
  if (!patchesList || !patchConfig) return;
  patchesList.innerHTML = '';
  
  if (!patchConfig.universes || Object.keys(patchConfig.universes).length === 0) {
    patchesList.innerHTML = '<div style="color: #9ca3af; padding: 10px;">No fixtures patched yet.</div>';
    return;
  }
  
  Object.entries(patchConfig.universes).forEach(([universe, universeData]) => {
    if (!universeData.fixtures || universeData.fixtures.length === 0) return;
    
    universeData.fixtures.forEach(fixture => {
      const patchCard = document.createElement('div');
      patchCard.style.cssText = 'border: 1px solid #374151; padding: 10px; margin-bottom: 10px; border-radius: 8px; background: #111827;';
      
      const fixtureType = fixtureTypes && fixtureTypes[fixture.type] ? fixtureTypes[fixture.type].name : fixture.type;
      const channelCount = fixtureTypes && fixtureTypes[fixture.type] ? fixtureTypes[fixture.type].channels.length : '?';
      
      patchCard.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: start;">
          <div style="flex: 1;">
            <div style="font-weight: 600; margin-bottom: 5px;">${fixture.id}</div>
            <div style="font-size: 12px; color: #9ca3af;">
              <div>Universe: ${universe} | Address: ${fixture.start_address} (${channelCount} ch)</div>
              <div>Type: ${fixtureType}</div>
              ${fixture.description ? `<div style="margin-top: 5px;">${fixture.description}</div>` : ''}
            </div>
          </div>
          <div style="display: flex; gap: 5px;">
            <button class="color-btn secondary" style="padding: 6px 12px; font-size: 12px;" onclick="editPatch('${universe}', '${fixture.id}')">Edit</button>
            <button class="color-btn secondary" style="padding: 6px 12px; font-size: 12px; background: #7f1d1d; border-color: #991b1b;" onclick="deletePatch('${universe}', '${fixture.id}')">Delete</button>
          </div>
        </div>
      `;
      patchesList.appendChild(patchCard);
    });
  });
}

function renderNodes() {
  const nodesList = document.getElementById('nodes-list');
  if (!nodesList) return;
  nodesList.innerHTML = '';
  
  artnetConfig.nodes.forEach(node => {
    const nodeCard = document.createElement('div');
    nodeCard.style.cssText = 'border: 1px solid #374151; padding: 10px; margin-bottom: 10px; border-radius: 8px; background: #111827;';
    nodeCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: start;">
        <div style="flex: 1;">
          <div style="font-weight: 600; margin-bottom: 5px;">${node.name}</div>
          <div style="font-size: 12px; color: #9ca3af;">
            <div>ID: ${node.id}</div>
            <div>IP: ${node.ip}</div>
            <div>Universes: ${node.universes.join(', ')}</div>
            ${node.description ? `<div style="margin-top: 5px;">${node.description}</div>` : ''}
            <div style="margin-top: 5px;">
              <span style="padding: 2px 8px; border-radius: 999px; background: ${node.enabled ? '#065f46' : '#7f1d1d'}; font-size: 10px;">
                ${node.enabled ? 'Enabled' : 'Disabled'}
              </span>
              ${node.broadcast ? '<span style="padding: 2px 8px; border-radius: 999px; background: #1e40af; font-size: 10px; margin-left: 5px;">Broadcast</span>' : ''}
            </div>
          </div>
        </div>
        <div style="display: flex; gap: 5px;">
          <button class="color-btn secondary" style="padding: 6px 12px; font-size: 12px;" onclick="editNode('${node.id}')">Edit</button>
          <button class="color-btn secondary" style="padding: 6px 12px; font-size: 12px; background: #7f1d1d; border-color: #991b1b;" onclick="deleteNode('${node.id}')">Delete</button>
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
    mappingCard.style.cssText = 'border: 1px solid #374151; padding: 10px; margin-bottom: 10px; border-radius: 8px; background: #111827;';
    mappingCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: start;">
        <div style="flex: 1;">
          <div style="font-weight: 600; margin-bottom: 5px;">DMX Universe ${dmxUniverse}</div>
          <div style="font-size: 12px; color: #9ca3af;">
            <div>Node: ${mapping.node_id}</div>
            <div>ArtNet Universe: ${mapping.artnet_universe}</div>
            <div style="margin-top: 5px;">
              <span style="padding: 2px 8px; border-radius: 999px; background: ${mapping.output_mode === 'artnet' ? '#1e40af' : '#374151'}; font-size: 10px;">
                ${mapping.output_mode}
              </span>
            </div>
          </div>
        </div>
        <div style="display: flex; gap: 5px;">
          <button class="color-btn secondary" style="padding: 6px 12px; font-size: 12px;" onclick="editMapping('${dmxUniverse}')">Edit</button>
          <button class="color-btn secondary" style="padding: 6px 12px; font-size: 12px; background: #7f1d1d; border-color: #991b1b;" onclick="deleteMapping('${dmxUniverse}')">Delete</button>
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

// Patch CRUD
window.editPatch = function(universe, fixtureId) {
  const fixture = patchConfig.universes[universe]?.fixtures.find(f => f.id === fixtureId);
  if (!fixture) return;
  
  document.getElementById('patch-modal-title').textContent = 'Edit Patched Fixture';
  document.getElementById('patch-modal-original-universe').value = universe;
  document.getElementById('patch-modal-original-id').value = fixtureId;
  document.getElementById('patch-universe').value = universe;
  document.getElementById('patch-id').value = fixture.id;
  document.getElementById('patch-id').disabled = true;
  document.getElementById('patch-address').value = fixture.start_address;
  document.getElementById('patch-description').value = fixture.description || '';
  
  // Populate fixture types dropdown
  const typeSelect = document.getElementById('patch-type');
  typeSelect.innerHTML = '<option value="">Select fixture type...</option>';
  if (fixtureTypes) {
    Object.entries(fixtureTypes).forEach(([typeId, typeData]) => {
      const option = document.createElement('option');
      option.value = typeId;
      option.textContent = typeData.name || typeId;
      if (typeId === fixture.type) {
        option.selected = true;
      }
      typeSelect.appendChild(option);
    });
  }
  
  document.getElementById('patch-modal').style.display = 'flex';
};

window.deletePatch = function(universe, fixtureId) {
  if (confirm('Delete fixture "' + fixtureId + '" from universe ' + universe + '?')) {
    if (patchConfig.universes[universe]) {
      patchConfig.universes[universe].fixtures = patchConfig.universes[universe].fixtures.filter(f => f.id !== fixtureId);
      // Clean up empty universes
      if (patchConfig.universes[universe].fixtures.length === 0) {
        delete patchConfig.universes[universe];
      }
    }
    savePatchConfig();
    renderPatches();
  }
};

// Node CRUD
window.editNode = function(nodeId) {
  const node = artnetConfig.nodes.find(n => n.id === nodeId);
  if (!node) return;
  
  document.getElementById('node-modal-title').textContent = 'Edit Node';
  document.getElementById('node-modal-id').value = nodeId;
  document.getElementById('node-id').value = node.id;
  document.getElementById('node-id').disabled = true;
  document.getElementById('node-name').value = node.name;
  document.getElementById('node-ip').value = node.ip;
  document.getElementById('node-universes').value = node.universes.join(', ');
  document.getElementById('node-description').value = node.description || '';
  document.getElementById('node-broadcast').checked = node.broadcast;
  document.getElementById('node-enabled').checked = node.enabled;
  
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
    colorCard.style.cssText = 'border: 1px solid #374151; padding: 10px; margin-bottom: 10px; border-radius: 8px; background: #111827;';
    
    // Convert RGBW to RGB for preview
    const r = Math.round(color.r * 255);
    const g = Math.round(color.g * 255);
    const b = Math.round(color.b * 255);
    const rgbColor = `rgb(${r}, ${g}, ${b})`;
    
    colorCard.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="flex: 1;">
          <div style="font-weight: 600; margin-bottom: 5px;">${colorName}</div>
          <div style="font-size: 12px; color: #9ca3af;">
            <div>R: ${color.r.toFixed(2)}, G: ${color.g.toFixed(2)}, B: ${color.b.toFixed(2)}, W: ${color.w.toFixed(2)}</div>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
          <div style="width: 40px; height: 40px; border-radius: 4px; border: 1px solid #374151; background: ${rgbColor};"></div>
          <div>
            <button class="small" onclick="editColor('${colorName}')">Edit</button>
            <button class="small danger" onclick="deleteColor('${colorName}')">Delete</button>
          </div>
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

// Event listeners
let eventListenersInitialized = false;

function initConfigEventListeners() {
  // Prevent duplicate event listener bindings
  if (eventListenersInitialized) return;
  eventListenersInitialized = true;
  
  // Patch modal handlers
  const addPatchBtn = document.getElementById('add-patch-btn');
  if (addPatchBtn) {
    addPatchBtn.addEventListener('click', () => {
      document.getElementById('patch-modal-title').textContent = 'Add Patched Fixture';
      document.getElementById('patch-modal-original-universe').value = '';
      document.getElementById('patch-modal-original-id').value = '';
      document.getElementById('patch-universe').value = '1';
      document.getElementById('patch-id').value = '';
      document.getElementById('patch-id').disabled = false;
      document.getElementById('patch-type').value = '';
      document.getElementById('patch-address').value = '';
      document.getElementById('patch-description').value = '';
      
      // Populate fixture types dropdown
      const typeSelect = document.getElementById('patch-type');
      typeSelect.innerHTML = '<option value="">Select fixture type...</option>';
      if (fixtureTypes) {
        Object.entries(fixtureTypes).forEach(([typeId, typeData]) => {
          const option = document.createElement('option');
          option.value = typeId;
          option.textContent = typeData.name || typeId;
          typeSelect.appendChild(option);
        });
      }
      
      document.getElementById('patch-modal').style.display = 'flex';
    });
  }

  const patchSaveBtn = document.getElementById('patch-modal-save');
  if (patchSaveBtn) {
    patchSaveBtn.addEventListener('click', () => {
      const isEdit = document.getElementById('patch-modal-original-id').value !== '';
      const universe = document.getElementById('patch-universe').value.trim();
      const fixtureId = document.getElementById('patch-id').value.trim();
      const fixtureType = document.getElementById('patch-type').value;
      const address = parseInt(document.getElementById('patch-address').value);
      const description = document.getElementById('patch-description').value.trim();
      
      if (!universe || !fixtureId || !fixtureType || isNaN(address) || address < 1 || address > 512) {
        showToast('Please fill all required fields with valid values', 'warning');
        return;
      }
      
      const fixture = {
        id: fixtureId,
        type: fixtureType,
        start_address: address,
        description: description
      };
      
      // Initialize universe if it doesn't exist
      if (!patchConfig.universes) {
        patchConfig.universes = {};
      }
      if (!patchConfig.universes[universe]) {
        patchConfig.universes[universe] = { fixtures: [] };
      }
      
      if (isEdit) {
        const origUniverse = document.getElementById('patch-modal-original-universe').value;
        const origId = document.getElementById('patch-modal-original-id').value;
        
        // Remove from old universe if universe changed
        if (origUniverse !== universe && patchConfig.universes[origUniverse]) {
          patchConfig.universes[origUniverse].fixtures = patchConfig.universes[origUniverse].fixtures.filter(f => f.id !== origId);
        }
        
        // Find and update or add
        const existingIndex = patchConfig.universes[universe].fixtures.findIndex(f => f.id === origId);
        if (existingIndex !== -1) {
          patchConfig.universes[universe].fixtures[existingIndex] = fixture;
        } else {
          // Check for duplicate ID in new universe
          if (patchConfig.universes[universe].fixtures.some(f => f.id === fixtureId)) {
            showToast('Fixture ID already exists in this universe', 'warning');
            return;
          }
          patchConfig.universes[universe].fixtures.push(fixture);
        }
      } else {
        // Check for duplicate ID
        if (patchConfig.universes[universe].fixtures.some(f => f.id === fixtureId)) {
          showToast('Fixture ID already exists in this universe', 'warning');
          return;
        }
        patchConfig.universes[universe].fixtures.push(fixture);
      }
      
      document.getElementById('patch-modal').style.display = 'none';
      savePatchConfig();
      renderPatches();
    });
  }

  const patchCancelBtn = document.getElementById('patch-modal-cancel');
  if (patchCancelBtn) {
    patchCancelBtn.addEventListener('click', () => {
      document.getElementById('patch-modal').style.display = 'none';
    });
  }
  
  const addNodeBtn = document.getElementById('add-node-btn');
  if (addNodeBtn) {
    addNodeBtn.addEventListener('click', () => {
      document.getElementById('node-modal-title').textContent = 'Add Node';
      document.getElementById('node-modal-id').value = '';
      document.getElementById('node-id').value = '';
      document.getElementById('node-id').disabled = false;
      document.getElementById('node-name').value = '';
      document.getElementById('node-ip').value = '';
      document.getElementById('node-universes').value = '';
      document.getElementById('node-description').value = '';
      document.getElementById('node-broadcast').checked = false;
      document.getElementById('node-enabled').checked = true;
      
      document.getElementById('node-modal').style.display = 'flex';
    });
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
      document.getElementById('mapping-modal').style.display = 'flex';
    });
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

  // Load config when Config tab is activated
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      if (tab.dataset.tab === 'config') {
        if (!artnetConfig) {
          loadArtNetConfig();
          initConfigEventListeners();
        }
        if (!fixtureTypes) {
          loadFixtureTypes();
        }
        if (!patchConfig) {
          loadPatchConfig();
        }
        // Always reload colors to pick up manual changes
        loadColorsConfig();
      }
    });
  });
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initConfigEventListeners);
} else {
  initConfigEventListeners();
}
