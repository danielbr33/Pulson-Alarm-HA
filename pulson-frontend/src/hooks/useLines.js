import { useState, useEffect } from "react";

export function useLines(hass) {
  const [lines, setLines] = useState([]);

  useEffect(() => {
    if (!hass) return;

    const states = hass.states;

    const lineNumbers = new Set();

    // Zbieramy numery linii na podstawie encji
    Object.keys(states).forEach((entity_id) => {
      const match = entity_id.match(/^(sensor|switch)\.linia_(\d+)_/);
      if (match) {
        lineNumbers.add(match[2]); // np. "1", "2", "3"
      }
    });

    const result = Array.from(lineNumbers).map((num) => {
      const id = String(num).padStart(2, "0"); // linia_01, linia_02...

      const stateEntity = states[`sensor.linia_${num}_stan`];
      const lockEntity = states[`switch.linia_${num}_blokada`];

      return {
        id,
        name: `Linia ${id}`,
        status: stateEntity?.state ?? "unknown",
        statusEntityId: stateEntity?.entity_id,
        isLocked: lockEntity?.state === "on",
        lockEntityId: lockEntity?.entity_id,
      };
    });

    setLines(result);
  }, [hass]);

  return lines;
}
