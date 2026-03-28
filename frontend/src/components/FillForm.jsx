import { useState } from 'react'

export default function FillForm({onSubmit}) {
    
    const [name, setName] = useState("")
    const [role, setRole] = useState("")
    const [contextFile, setContextFile] = useState(null)
    const [submitted, setSubmitted] = useState(false)

    const handleFile = (e) => {
        const file = e.target.files[0]
        if (file) setContextFile(file.path)
    }

    const handleSubmit = () => {
        setSubmitted(true)
        if (!name.trim() || !role.trim()) return
        onSubmit({ name, role, contextFile })
    }

    return (
        <div>
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
            <div style={{ marginBottom: 8 }}>
                <div className="label">Context File <span style={{ textTransform: 'none', opacity: 0.5 }}>(optional — .txt, .md, .pdf)</span></div>
                <input type="file" accept=".txt,.md,.pdf" onChange={handleFile} style={{ WebkitAppRegion: "no-drag", color: "rgba(255,255,255,0.6)", fontSize: 11, width: "100%" }} />
                {contextFile && <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", marginTop: 2 }}>{contextFile}</div>}
            </div>
            <button className="btn-primary" onClick={handleSubmit}>Start</button>
        </div>
    )
}
