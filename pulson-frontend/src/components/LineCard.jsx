import { FaBell, FaDotCircle, FaRegDotCircle } from "react-icons/fa";
import "./LineCard.css";

export function LineCard({ line, onToggleBlock }) {
  const isBlockEnabled = line.block_enable === "1";
  const isBlocked = line.block === "1";
  // Przykładowy status – możesz rozwinąć logikę na podstawie danych
  const statusText = isBlocked ? "Zamknięta" : "Otwarta";

  // Ikona w zależności od stanu/blokady
  let icon = <FaRegDotCircle size={28} color="#ff5722" />;
  if (isBlocked) icon = <FaDotCircle size={28} color="#ff5722" />;
  if (!isBlockEnabled) icon = <FaBell size={28} color="#ff5722" />;

  return (
    <div className="line-card">
      <div className="line-card__icon">{icon}</div>
      <div className="line-card__info">
        <div className="line-card__header">
          <span className="line-card__name">Linia {line.id}</span>
        </div>
        <div className="line-card__status">{statusText}</div>
      </div>
      <button
        className="line-card__button"
        onClick={onToggleBlock}
        disabled={!isBlockEnabled}
      >
        {isBlocked ? "Odblokuj" : "Zablokuj"}
      </button>
    </div>
  );
}
