import { LineCard } from "./components/LineCard";
import { PartitionCard } from "./components/PartitionCard";
import { useLines, usePartitions } from "./hooks/useLines";
import "./App.css";

function App({ hass }) {
  const lines = useLines(hass);
  const partitions = usePartitions(hass);

  const toggleBlock = (index, { block }) => {
    if (!hass) return;
    hass.callService(
      "switch",
      block === "1" ? "turn_off" : "turn_on",
      { entity_id: `switch.linia_${index}_blokada` },
    );
  };

  const armPartition = (id) => {
    if (!hass) return;
    hass.callService("alarm_control_panel", "alarm_arm_away", { entity_id: `alarm_control_panel.partycja_${id}` });
  };
  const armNightPartition = (id) => {
    if (!hass) return;
    hass.callService("alarm_control_panel", "alarm_arm_night", { entity_id: `alarm_control_panel.partycja_${id}` });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '32px' }}>
      <div className="partitions-panel lines-grid">
        {partitions.map((partition) => (
          <PartitionCard
            key={partition.id}
            partition={partition}
            onArm={() => armPartition(partition.id)}
            onArmNight={() => armNightPartition(partition.id)}
          />
        ))}
      </div>
      <div className="lines-panel lines-grid">
        {Object.entries(lines).map(([index, line]) => (
          <LineCard
            key={index}
            line={line}
            onToggleBlock={() => toggleBlock(index, line)}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
