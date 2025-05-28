class PulsonLineCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error("Wymagana encja");
    this._config = config;
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    const entity = hass.states[this._config.entity];
    if (!entity) return;

    const state = entity.state;
    const attrs = entity.attributes;
    const block = attrs.block ? "✅" : "❌";
    const blockEnable = attrs.block_enable ? "✅" : "❌";

    this.shadowRoot.innerHTML = `
        <ha-card header="Linia: ${this._config.entity}">
          <div style="padding: 16px;">
            <div><strong>Status:</strong> ${state}</div>
            <div><strong>Blokada:</strong> ${block}</div>
            <div><strong>Możliwość blokady:</strong> ${blockEnable}</div>
          </div>
        </ha-card>
      `;
  }

  getCardSize() {
    return 2;
  }
}

customElements.define("line-card", PulsonLineCard);
