export function LineCard({ line, hass }) {
  const toggleLock = () => {
    hass.callService("switch", line.isLocked ? "turn_off" : "turn_on", {
      entity_id: line.lockEntityId,
    });
  };

  return (
    <div className="line-card">
      <h3>{line.name}</h3>
      <p>Status: <strong>{line.status}</strong></p>
      <p>Blokada: <strong>{line.isLocked ? "Włączona" : "Wyłączona"}</strong></p>
      <button onClick={toggleLock}>
        {line.isLocked ? "Odblokuj" : "Zablokuj"}
      </button>
    </div>
  );
}
