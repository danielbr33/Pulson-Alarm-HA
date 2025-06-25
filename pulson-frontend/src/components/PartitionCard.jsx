import React from "react";
import { FaLock } from "react-icons/fa";
import "./LineCard.css";

export function PartitionCard({ partition, onArm, onArmNight }) {
  const { name, status, ready, night_mode } = partition;
  // Status tekstowy
  const statusText = status === 1 ? "Uzbrojona" : "Rozbrojona";

  return (
    <div className="line-card">
      <div className="line-card__icon">
        <FaLock size={28} color="#1a237e" />
      </div>
      <h3 className="line-card__header">{name}</h3>
      <span className="line-card__status">{statusText}</span>
      <button
        className="line-card__button"
        disabled={!ready}
        onClick={onArm}
      >
        Uzbrój
      </button>
      {night_mode && (
        <button
          className="line-card__button"
          disabled={!ready}
          onClick={onArmNight}
        >
          Uzbrój noc
        </button>
      )}
    </div>
  );
} 