import { FaBell, FaDotCircle, FaRegDotCircle } from "react-icons/fa";
import "./LineCard.css";

export function LineCard({ line, onToggleBlock }) {
  const { id, block_enable, block } = line;
  const isBlocked  = block === "1";
  const disabled   = block_enable !== "1";

  const status = isBlocked ? "Zamknięta" : "Otwarta";
  const icon = disabled
    ? <FaBell size={28} color="#ff5722" />
    : isBlocked
      ? <FaDotCircle size={28} color="#ff5722" />
      : <FaRegDotCircle size={28} color="#ff5722" />;

  return (
    <div className="line-card">
      <div className="line-card__icon">{icon}</div>

      <h3 className="line-card__header">Linia&nbsp;{id}</h3>
      <span className="line-card__status">{status}</span>

      <button
        className="line-card__button"
        disabled={disabled}
        onClick={onToggleBlock}
      >
        {isBlocked ? "Odblokuj" : "Zablokuj"}
      </button>
    </div>
  );
}
