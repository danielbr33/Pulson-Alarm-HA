import { LineCard } from "./components/LineCard";
import { useLines } from "./hooks/useLines";
import "./App.css";

function App({ hass }) {
  const lines = useLines(hass);

  const toggleBlock = (index, { block }) => {
    if (!hass) return;
    hass.callService(
      "switch",
      block === "1" ? "turn_off" : "turn_on",
      { entity_id: `switch.linia_${index}_blokada` },
    );
  };

  return (
    <div className="lines-grid">
      {Object.entries(lines).map(([index, line]) => (
        <LineCard
          key={index}
          line={line}
          onToggleBlock={() => toggleBlock(index, line)}
        />
      ))}
    </div>
  );
}

export default App;
