export default function ExpandedWindow({ question, answer, onDismiss }) {
    return (
        <div id="question-section" className="visible">
            <div className="label">Someone's asking you</div>
            <div id="transcript-text">{question}</div>
            <div className="label" style={{ marginBottom: 6 }}>Suggested response</div>
            <div id="answer-text">{answer}</div>
            <button onClick={onDismiss}>Dismiss</button>
        </div>
    )
}
