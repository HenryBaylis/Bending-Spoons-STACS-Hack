import { useState } from 'react'

export default function FillForm({onSubmit, onClose}) {
    
    const [name, setName] = useState("")
    const [role, setRole] = useState("")
    const [submitted, setSubmitted] = useState(false)

    const handleSubmit = () => {
        setSubmitted(true)
        if (!name.trim() || !role.trim()) return
        onSubmit({name, role})
    }

    return (
        <div id="card" style={{ position: "relative" }}>
            <button onClick={onClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
            <div className="label">Setup</div>
            <div style={{ marginBottom: 8 }}>
                <div className="label">Name</div>
                <input name="nameInput" value={name} onChange={e => setName(e.target.value)} style={{ WebkitAppRegion: "no-drag", background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 6, color: "#fff", fontSize: 12, padding: "4px 8px", width: "100%" }} />
                {submitted && !name.trim() && <span style={{ color: "#f87171", fontSize: 11 }}>Required</span>}
            </div>
            <div style={{ marginBottom: 8 }}>
                <div className="label">Role</div>
                <input name="roleInput" value={role} onChange={e => setRole(e.target.value)} style={{ WebkitAppRegion: "no-drag", background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 6, color: "#fff", fontSize: 12, padding: "4px 8px", width: "100%" }} />
                {submitted && !role.trim() && <span style={{ color: "#f87171", fontSize: 11 }}>Required</span>}
            </div>
            <button onClick={handleSubmit}>Start</button>
        </div>
    )
}
