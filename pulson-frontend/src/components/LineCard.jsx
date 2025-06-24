
export function LineCard({ entity }) {
    return (
      <div className="line-card">
        <h3>{entity.attributes.friendly_name || entity.entity_id}</h3>
        <p>Status: <strong>{entity.state}</strong></p>
        {/* Dodaj tu więcej atrybutów, np. blokada, ikonę */}
      </div>
    );
  }
  