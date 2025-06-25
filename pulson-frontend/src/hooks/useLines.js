import { useState, useEffect } from "react";

export function useLines(hass) {
  const [lines, setLines] = useState([]);

  useEffect(() => {
    if (!hass) return;

    // Pobierz dane o liniach z własnego endpointu
    hass.callApi("GET", "pulson_alarm/lines").then((data) => {
      // Zakładamy, że data to tablica/dict linii
      setLines(
        Object.entries(data).map(([id, line]) => ({
          id,
          name: line.name || `Linia ${id}`,
          block: line.block,
          block_enable: line.block_enable,
        }))
      );
    });
  }, [hass]);

  return lines;
}
