class PulsonLineCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity_base) {
      throw new Error("Wymagany parametr 'entity_base'");
    }

    this._config = config;
    const root = this.attachShadow({ mode: "open" });

    root.innerHTML = `
      <style>
        .line-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          border-bottom: 1px solid #ccc;
        }
        .status {
          font-weight: bold;
        }
        .controls {
          display: flex;
          gap: 10px;
        }
      </style>
      <ha-card header="${config.title || config.entity_base}">
        <div class="line-row">
          <div class="status" id="status">Status: brak</div>
          <div class="controls">
            <ha-entity-toggle id="block" entity="${config.entity_base}_block"></ha-entity-toggle>
          </div>
        </div>
        <div style="padding: 10px; font-size: 12px;">
          Możliwość blokady: <span id="block_enable">brak</span>
        </div>
      </ha-card>
    `;
  }

  set hass(hass) {
    this._hass = hass;
    const base = this._config.entity_base;
    const statusEl = this.shadowRoot.getElementById("status");
    const blockEnableEl = this.shadowRoot.getElementById("block_enable");
    const blockToggle = this.shadowRoot.getElementById("block");

    const status = hass.states[`${base}_status`];
    const blockEnable = hass.states[`${base}_block_enable`];

    if (status) {
      statusEl.textContent = `Status: ${status.state}`;
    }

    if (blockEnable) {
      blockEnableEl.textContent = blockEnable.state;
    }

    if (blockToggle) {
      blockToggle.hass = hass;
    }
  }

  getCardSize() {
    return 2;
  }
}

customElements.define("pulson-line-card", PulsonLineCard);

// =======================
// === CONFIG EDITOR ====
// =======================
class PulsonLineCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getConfig() {
    return {
      type: "custom:pulson-line-card",
      entity_base: this._config.entity_base,
      title: this._config.title,
    };
  }

  render() {
    if (!this._hass || !this.shadowRoot) return;

    const lineEntities = Object.keys(this._hass.states)
      .filter((eid) => eid.endsWith("_status"))
      .map((eid) => eid.replace("_status", ""));

    const selected = this._config.entity_base || "";
    const title = this._config.title || "";

    this.shadowRoot.innerHTML = `
      <style>
        .form-row {
          display: flex;
          flex-direction: column;
          margin-bottom: 12px;
        }
        label {
          font-weight: bold;
          margin-bottom: 4px;
        }
        select, input {
          padding: 6px;
          font-size: 14px;
        }
      </style>
      <div class="form-row">
        <label for="entity_base">Baza encji (np. sensor.linia_1):</label>
        <select id="entity_base">
          ${lineEntities.map(e => `<option value="${e}" ${e === selected ? "selected" : ""}>${e}</option>`).join("")}
        </select>
      </div>
      <div class="form-row">
        <label for="title">Tytuł:</label>
        <input id="title" type="text" value="${title}" placeholder="np. Linia 1" />
      </div>
    `;

    this.shadowRoot.getElementById("entity_base").addEventListener("change", (e) => {
      this._config.entity_base = e.target.value;
      this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this.getConfig() } }));
    });

    this.shadowRoot.getElementById("title").addEventListener("input", (e) => {
      this._config.title = e.target.value;
      this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: this.getConfig() } }));
    });
  }

  connectedCallback() {
    this.attachShadow({ mode: "open" });
    this.render();
  }
}

customElements.define("pulson-line-card-editor", PulsonLineCardEditor);

// =======================
// === REQUIRED METADATA ====
// =======================
PulsonLineCard.getConfigElement = () => {
  return document.createElement("pulson-line-card-editor");
};

PulsonLineCard.getStubConfig = (hass) => {
  const base = Object.keys(hass.states).find(e => e.endsWith("_status"))?.replace("_status", "") || "sensor.linia_1";
  return {
    type: "custom:pulson-line-card",
    entity_base: base,
    title: `Linia ${base.replace(/\D/g, "")}`
  };
};
