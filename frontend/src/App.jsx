import { useState, useEffect } from 'react'
import ExpandedWindow from "./components/ExpandedWindow";

const { ipcRenderer } = require('electron')

export default function App() {
  const [visible, setVisible] = useState(false)
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")

  const dismiss = () => setVisible(false)

  return (
    <div id="expanded-window">
      {visible && (
        <ExpandedWindow
          question={question}
          answer={answer}
          onDismiss={dismiss}
        />
      )}
    </div>
  )
}
