import React, { useEffect, useState } from "react";

function App() {
  const [hass, setHass] = useState(null);
  const [lines, setLines] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (window.parent && window.parent.hass) {
        setHass(window.parent.hass);
        clearInterval(interval);
      }
    }, 300);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!hass) return;
    const allEntities = hass.states;
    const lineIds = Object.keys(allEntities)
      .filter((eid) => eid.startsWith("sensor.linia_") && eid.endsWith("_stan"))
      .map((eid) => eid.replace("sensor.", "").replace("_stan", ""));

    const newLines = lineIds.map((id) => {
      const status = allEntities[`sensor.${id}_stan`]?.state;
      const blockEnable = allEntities[`sensor.${id}_blokada_dostepna`]?.state;
      const blockSwitch = allEntities[`switch.${id}_blokada`];
      return {
        id,
        status,
        blockEnable,
        blockSwitch,
      };
    });
    setLines(newLines);
  }, [hass]);

  const toggleBlock = (entityId, currentState) => {
    if (!hass) return;
    hass.callService("switch", currentState ? "turn_off" : "turn_on", {
      entity_id: entityId,
    });
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Pulson Alarm - Linie</h1>
      <div className="grid grid-cols-1 gap-4">
        {lines.map((line) => (
          <div key={line.id} className="p-4 rounded-2xl shadow bg-white border">
            <div className="grid grid-cols-4 gap-4 items-center">
              <div>
                <div className="font-semibold">Linia {line.id}</div>
                <div className="text-sm text-gray-500">Stan: {line.status}</div>
              </div>
              <div>
                Blokada dostępna:
                <span className="ml-1 font-medium">
                  {line.blockEnable === "Tak" ? "✔️" : "❌"}
                </span>
              </div>
              <div>
                Blokada:
                <span className="ml-1 font-medium">
                  {line.blockSwitch?.state === "on" ? "Włączona" : "Wyłączona"}
                </span>
              </div>
              <div>
                <button
                  onClick={() =>
                    toggleBlock(
                      line.blockSwitch.entity_id,
                      line.blockSwitch.state === "on"
                    )
                  }
                  disabled={line.blockEnable !== "Tak"}
                  className="px-3 py-1 rounded bg-blue-500 text-white disabled:opacity-50"
                >
                  {line.blockSwitch?.state === "on" ? "Wyłącz blokadę" : "Włącz blokadę"}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
