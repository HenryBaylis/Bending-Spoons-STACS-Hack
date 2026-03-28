export default function ExpandedWindow({ question, answer, onDismiss, onClose }) {
    return (
        <div id="question-section" className="visible" style={{ position: "relative" }}>
            <button onClick={onClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
            <div className="label">Someone Asking you</div>
            <div id="question-text">{question}</div>
            <div className="label" style={{ marginBottom: 6 }}>Suggested Response</div>
            <div id="answer-text">{answer}</div>
            <button onClick={onDismiss}>Dismiss</button>
        </div>
    )
}
