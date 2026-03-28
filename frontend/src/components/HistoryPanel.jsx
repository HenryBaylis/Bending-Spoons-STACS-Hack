export default function HistoryPanel({ history }) {
    if (!history.length) return null
    return (
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: 8, marginTop: 2 }}>
            <div className="label">History</div>
            <div style={{ maxHeight: 130, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
                {history.map((item, i) => (
                    <div key={i} style={{
                        paddingBottom: 6,
                        borderBottom: i < history.length - 1 ? "1px solid rgba(255,255,255,0.06)" : "none"
                    }}>
                        <div style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", marginBottom: 2, overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>
                            "{item.question}"
                        </div>
                        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.55)", lineHeight: 1.4 }}>
                            {item.answer}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
