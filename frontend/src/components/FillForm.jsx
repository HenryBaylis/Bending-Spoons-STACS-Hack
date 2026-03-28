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
        <div id="form-section" style={{ position: "relative" }}>
            <button onClick={onClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
            <div>Please fill your information</div>
            <div>
                <label>Name: <input name="nameInput" value={name} onChange={e => setName(e.target.value)} style={{ WebkitAppRegion: "no-drag" }} /></label>
                {submitted && !name.trim() && <span style={{ color: "red", fontSize: 11, marginLeft: 6 }}>Required</span>}
            </div>
            <div>
                <label>Role: <input name="roleInput" value={role} onChange={e => setRole(e.target.value)} style={{ WebkitAppRegion: "no-drag" }} /></label>
                {submitted && !role.trim() && <span style={{ color: "red", fontSize: 11, marginLeft: 6 }}>Required</span>}
            </div>
            <button onClick={handleSubmit}>Enter</button>
        </div>
    )
}
