import { useState, useEffect } from "react";

export function useLines(hass) {
  const [lines, setLines] = useState([]);

  useEffect(() => {
    // Jeśli nie ma hass, pobierz dane z mocka
    if (!hass) {
      fetch(`${import.meta.env.BASE_URL}mockData.json`)
        .then((res) => {
          if (!res.ok) {
            console.error("Nie znaleziono pliku mockData.json!", res.status, res.statusText);
            throw new Error("Brak pliku mockData.json");
          }
          return res.json();
        })
        .then((data) => {
          const linesData = data.Lines || {};
          setLines(
            Object.entries(linesData).map(([id, line]) => ({
              id,
              name: line.name || `Linia ${id}`,
              block: line.block,
              block_enable: line.block_enable,
            }))
          );
        })
        .catch((err) => {
          console.error("Błąd podczas pobierania lub parsowania mockData.json:", err);
        });
      return;
    }

    // Jeśli jest hass, pobierz dane z API HA
    hass.callApi("GET", "pulson_alarm/lines").then((data) => {
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
