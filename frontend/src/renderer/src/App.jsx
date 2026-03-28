import { useState, useEffect, useRef } from 'react'
import FillForm from '../../components/FillForm'
import MockWindow from '../../components/MockWindow'
import ExpandedWindow from '../../components/ExpandedWindow'

export default function App() {
  const [stage, setStage] = useState('form') // 'form' | 'mock' | 'expanded'
  const [question, setQuestion] = useState("Can you tell us about yourself?")
  const [answer, setAnswer] = useState("I am a software engineer with experience in React and Electron.")
  const containerRef = useRef(null)

  const handleClose = () => window.close()

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const observer = new ResizeObserver(() => {
      window.api?.resizeWindow(el.offsetHeight)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [stage])

  useEffect(() => {
    if (stage === 'mock') {
      const timer = setTimeout(() => setStage('expanded'), 5000)
      return () => clearTimeout(timer)
    }
  }, [stage])

  const handleStart = (profile) => {
    window.api.startMeeting(profile)
    setStage('mock')
  }

  if (stage === 'form') {
    return <div ref={containerRef}><FillForm onSubmit={handleStart} onClose={handleClose} /></div>
  }

  return (
    <div ref={containerRef}>
      <MockWindow onClose={handleClose}>
        {stage === 'expanded' && (
          <ExpandedWindow
            question={question}
            answer={answer}
            onDismiss={() => setStage('mock')}
          />
        )}
      </MockWindow>
    </div>
  )
}
