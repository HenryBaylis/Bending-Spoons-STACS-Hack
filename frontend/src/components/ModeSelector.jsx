const MODES = ["Assertiveness", "Promise Maker", "Debate", "AFK"];

export default function ModeSelector({ modes, onChange }) {
  const toggle = (m) => {
    if (modes.includes(m)) {
      onChange(modes.filter((x) => x !== m));
    } else {
      onChange([...modes, m]);
    }
  };

  return (
    <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
      {MODES.map((m) => {
        const active = modes.includes(m);
        return (
          <button
            key={m}
            onClick={() => toggle(m)}
            style={{
              flex: 1,
              background: active ? "rgba(99,102,241,0.35)" : "rgba(255,255,255,0.06)",
              border: active ? "1px solid rgba(99,102,241,0.7)" : "1px solid rgba(255,255,255,0.1)",
              color: active ? "#fff" : "rgba(255,255,255,0.45)",
              borderRadius: 7,
              fontSize: 10,
              padding: "3px 0",
              cursor: "pointer",
              fontWeight: active ? 600 : 400,
              transition: "all 0.15s",
            }}
          >
            {m}
          </button>
        );
      })}
    </div>
  );
}
