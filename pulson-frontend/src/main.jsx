import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import LineCardCss from "./components/LineCard.css?inline";

class PulsonPanel extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._root = null;
  }

  set hass(hass) {
    this._hass = hass;
    this._root?.render(<App hass={this._hass} />);
  }

  connectedCallback() {
    if (this._root) return; // already initialised
    const container = document.createElement("div");
    const shadow = this.attachShadow({ mode: "open" });

    // Dodaj style do shadow DOM
    const style = document.createElement("style");
    style.textContent = LineCardCss;
    shadow.appendChild(style);

    shadow.appendChild(container);

    this._root = ReactDOM.createRoot(container);
    this._root.render(<App hass={this._hass} />);
  }

  disconnectedCallback() {
    this._root?.unmount();
    this._root = null;
  }
}

if (!customElements.get("pulson-alarm-panel")) {
  customElements.define("pulson-alarm-panel", PulsonPanel);
}