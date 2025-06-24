import React from "react";
import { useLineEntities } from "./hooks/useLineEntities";
import { LineCard } from "./components/LineCard";
import "./App.css";

function App({ hass }) {
  const lines = useLineEntities(hass);

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
        <LineCard key={line.entity_id} entity={line} />
      ))}
    </div>
  );
}

export default App;