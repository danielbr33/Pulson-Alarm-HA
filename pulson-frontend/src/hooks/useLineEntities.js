import { useEffect, useState } from "react";

/**
 * Zwraca listę encji sensor.linia_*_status na żywo.
 *
 * Hook wykorzystuje natywny obiekt `hass`,
 * który jest przekazywany z <PulsonPanel>.  Nie ma już połączenia
 * z haConnection ani home-assistant-js-websocket – HA odświeża prop
 * `hass` przy każdej zmianie stanu, więc wystarczy reagować na ten prop.
 */
export function useLineEntities(hass) {
  const [entities, setEntities] = useState([]);

  useEffect(() => {
    if (!hass) return;

    const linie = Object.values(hass.states).filter(
      (s) =>
        s.entity_id.startsWith("sensor.linia_") &&
        s.entity_id.endsWith("_stan")
    );
    setEntities(linie);
  }, [hass]);

  return entities;
}