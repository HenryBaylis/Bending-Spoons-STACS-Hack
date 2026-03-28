export default function ExpandedWindow({ question, answer, onDismiss }) {
    return (
        <>
            <div className="label">Someone Asking you</div>
            <div id="question-text">{question}</div>
            <div className="label" style={{ marginBottom: 6 }}>Suggested Response</div>
            <div id="answer-text">{answer}</div>
            <button onClick={onDismiss}>Dismiss</button>
        </>
    )
}
