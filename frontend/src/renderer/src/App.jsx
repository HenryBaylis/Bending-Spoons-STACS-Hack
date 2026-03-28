import { useState, useEffect } from 'react'
import FillForm from '../../components/FillForm'
import ExpandedWindow from '../../components/ExpandedWindow'

export default function App() {
  const [stage, setStage] = useState('form') // 'form' | 'mock' | 'expanded'
  const [question, setQuestion] = useState("Can you tell us about yourself?")
  const [answer, setAnswer] = useState("I am a software engineer with experience in React and Electron.")

  const handleClose = () => window.close()

  useEffect(() => {
    if (stage === 'mock') {
      const timer = setTimeout(() => setStage('expanded'), 5000)
      return () => clearTimeout(timer)
    }
  }, [stage])

  if (stage === 'form') {
    return <FillForm onSubmit={() => setStage('mock')} onClose={handleClose} />
  }

  return (
    <div id="question-section" className="visible" style={{ position: "relative", minHeight: 150, minWidth: 420 }}>
      <button onClick={handleClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
      {stage === 'expanded' && (
        <ExpandedWindow
          question={question}
          answer={answer}
          onDismiss={() => setStage('mock')}
          onClose={handleClose}
        />
      )}
    </div>
  )
}
