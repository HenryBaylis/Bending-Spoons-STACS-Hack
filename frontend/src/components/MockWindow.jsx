import HistoryPanel from './HistoryPanel'

export default function MockWindow({ onClose, children, history = [] }) {
    return (
        <div id="card" style={{ position: "relative" }}>
            <button onClick={onClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
            <div id="live-section">
                <div className="label"><span className="dot"></span>Live</div>
                <div id="live-text">—</div>
            </div>
            <div id="mention-section" style={{ display: "none", marginBottom: 10, borderLeft: "2px solid rgba(250,204,21,0.5)", paddingLeft: 8 }}>
                <div className="label">Mentioned</div>
                <div id="mention-text" style={{ fontSize: 12, color: "rgba(255,255,255,0.6)", lineHeight: 1.4 }}></div>
            </div>
            <div id="summary-section">
                <div className="label">Last summary</div>
                <div id="summary-text">—</div>
            </div>
            {children}
            <HistoryPanel history={history} />
        </div>
    )
}
