import { useState } from 'react'

export default function FillForm({onSubmit}) {
    
    const [name, setName] = useState("")
    const [role, setRole] = useState("")

    const handleSubmit = () => {
        onSubmit({name, role})
    }

    return (
        <div id="form-section">
            <label>
                Please fill your information
            </label>
            <label>
                Name: <input name="nameInput" />
            </label>
            <label>
                Role: <input name="roleInput" />
            </label>
            <button onClick={handleSubmit}>Enter</button>
        </div>
    )
}
