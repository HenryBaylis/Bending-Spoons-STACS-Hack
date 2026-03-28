import { useEffect } from 'react'

export default function MockWindow({ onExpand, onClose }) {
    useEffect(() => {
        const timer = setTimeout(() => {
            onExpand()
        }, 5000)
        return () => clearTimeout(timer)
    }, [])

    return (
        <div id="question-section" className="visible" style={{ position: "relative", minHeight: 150, minWidth: 420 }}>
            <button onClick={onClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
        </div>
    )
}
