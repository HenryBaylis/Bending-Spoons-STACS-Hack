import { useState } from 'react'

export default function FillForm({onSubmit, onClose}) {
    
    const [name, setName] = useState("")
    const [role, setRole] = useState("")

    const handleSubmit = () => {
        onSubmit({name, role})
    }

    return (
        <div id="form-section" style={{ position: "relative" }}>
            <button onClick={onClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
            <div>Please fill your information</div>
            <div><label>Name: <input name="nameInput" value={name} onChange={e => setName(e.target.value)} style={{ WebkitAppRegion: "no-drag" }} /></label></div>
            <div><label>Role: <input name="roleInput" value={role} onChange={e => setRole(e.target.value)} style={{ WebkitAppRegion: "no-drag" }} /></label></div>
            <button onClick={handleSubmit}>Enter</button>
        </div>
    )
}
