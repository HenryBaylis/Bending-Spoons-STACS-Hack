export default function MockWindow({ onClose, children }) {
    return (
        <div id="card" style={{ position: "relative" }}>
            <button onClick={onClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
            <div id="live-section">
                <div className="label"><span className="dot"></span>Live</div>
                <div id="live-text">—</div>
            </div>
            <div id="summary-section">
                <div className="label">Last summary</div>
                <div id="summary-text">—</div>
            </div>
            {children}
        </div>
    )
}
