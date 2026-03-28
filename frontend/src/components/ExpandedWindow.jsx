export default function ExpandedWindow({ question, answer, followUp, modes, onDismiss }) {
    return (
        <div id="question-section" className="visible">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                <div className="label" style={{ margin: 0 }}>Someone's asking you</div>
                {modes && modes.length > 0 && (
                    <div style={{ display: "flex", gap: 4 }}>
                        {modes.map((m) => (
                            <span key={m} style={{ fontSize: 10, background: "rgba(99,102,241,0.25)", border: "1px solid rgba(99,102,241,0.5)", borderRadius: 5, padding: "2px 7px", color: "rgba(180,180,255,0.9)", fontWeight: 600 }}>{m}</span>
                        ))}
                    </div>
                )}
            </div>
            <div id="transcript-text">{question}</div>
            <div className="label" style={{ marginBottom: 6 }}>Suggested response</div>
            <div id="answer-text">{answer}</div>
            {followUp && (
                <div style={{ marginTop: 10, borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: 8 }}>
                    <div className="label" style={{ marginBottom: 4 }}>Possible follow-up</div>
                    <div style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", lineHeight: 1.4, fontStyle: "italic" }}>{followUp}</div>
                </div>
            )}
            <button onClick={onDismiss} style={{ marginTop: 12 }}>Dismiss</button>
        </div>
    )
}
