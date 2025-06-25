import React from "react";
import { useLines } from "./hooks/useLines";
import { LineCard } from "./components/LineCard";
import "./App.css";

function App({ hass }) {
  const [linesData, setLinesData] = React.useState({});
  const lines = useLines(hass);

  // Funkcja do obsługi blokowania/odblokowania
  const handleToggleBlock = (index, line) => {
    if (!hass) return;
    const entityId = `switch.linia_${index}_blokada`;
    hass.callService("switch", line.block === "1" ? "turn_off" : "turn_on", {
      entity_id: entityId,
    });
  };

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
      {Object.entries(lines).map(([index, line]) => (
        <LineCard
          key={index}
          index={index}
          line={line}
          onToggleBlock={() => handleToggleBlock(index, line)}
        />
      ))}
    </div>
  );
}

export default App;