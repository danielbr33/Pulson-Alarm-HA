import React from "react";
import { useLines } from "./hooks/useLines";
import { LineCard } from "./components/LineCard";
import "./App.css";

function App({ hass }) {
  const lines = useLines(hass);

  // Przykład REST – jeden strzał po załadowaniu panelu
  React.useEffect(() => {
    if (!hass) return;
    (async () => {
      const conf = await hass.callApi("GET", "config");
      console.debug("Konfiguracja HA:", conf);
    })();
  }, [hass]);

  return (
    <div className="lines-grid">
      {lines.length === 0 && <p>Brak wykrytych linii.</p>}
      {lines.map((line) => (
        <LineCard key={line.id} line={line} hass={hass} />
      ))}
    </div>
  );
}

export default App;