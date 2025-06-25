export function LineCard({ line, onToggleBlock }) {
  const isBlockEnabled = line.block_enable === "1";
  const isBlocked = line.block === "1";

  return (
    <div className="line-card">
      <h3>
        Linia {line.id}: {line.name}
      </h3>
      <p>Blokada: <strong>{isBlocked ? "Włączona" : "Wyłączona"}</strong></p>
      <button
        onClick={onToggleBlock}
        disabled={!isBlockEnabled}
        style={{ opacity: isBlockEnabled ? 1 : 0.5, cursor: isBlockEnabled ? "pointer" : "not-allowed" }}
      >
        {isBlocked ? "Odblokuj" : "Zablokuj"}
      </button>
      {!isBlockEnabled && (
        <div style={{ fontSize: "0.9em", color: "#888" }}>
          Blokada niedostępna dla tej linii
        </div>
      )}
    </div>
  );
}
