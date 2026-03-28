import { useState } from 'react'
import FillForm from '../../components/FillForm'
import ExpandedWindow from '../../components/ExpandedWindow'

export default function App() {
  const [submitted, setSubmitted] = useState(false)
  const [visible, setVisible] = useState(true)
  const [question, setQuestion] = useState("Can you tell us about yourself?")
  const [answer, setAnswer] = useState("I am a software engineer with experience in React and Electron.")

  const handleClose = () => window.close()

  if (!submitted) {
    return <FillForm onSubmit={() => setSubmitted(true)} onClose={handleClose} />
  }

  return (
    <div id="expanded-window">
      {visible && (
        <ExpandedWindow
          question={question}
          answer={answer}
          onDismiss={() => setVisible(false)}
          onClose={handleClose}
        />
      )}
    </div>
  )
}
