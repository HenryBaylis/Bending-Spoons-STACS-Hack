export default function ExpandedWindow({ question, answer, followUp, onDismiss }) {
    return (
        <div id="question-section" className="visible">
            <div className="label">Someone's asking you</div>
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
