import React, { useEffect, useState } from "react";
const { ipcRenderer } = window.require("electron"); // Use contextBridge in production for safety

export default function App() {
  const [liveText, setLiveText] = useState("—");
  const [summaryText, setSummaryText] = useState("—");
  const [question, setQuestion] = useState({ transcript: "", answer: "" });
  const [questionVisible, setQuestionVisible] = useState(false);

  useEffect(() => {
    ipcRenderer.on("transcript", (_, data) => setLiveText(data.text));
    ipcRenderer.on("summary", (_, data) => setSummaryText(data.text));
    ipcRenderer.on("question", (_, data) => {
      setQuestion({ transcript: data.transcript, answer: data.answer });
      setQuestionVisible(true);
    });
    ipcRenderer.on("dismiss", () => setQuestionVisible(false));

    return () => {
      ipcRenderer.removeAllListeners("transcript");
      ipcRenderer.removeAllListeners("summary");
      ipcRenderer.removeAllListeners("question");
      ipcRenderer.removeAllListeners("dismiss");
    };
  }, []);

  const dismiss = () => {
    setQuestionVisible(false);
    ipcRenderer.send("dismiss");
  };

  return (
    <div id="card">
      <div id="live-section">
        <div className="label">
          <span className="dot"></span> Live
        </div>
        <div id="live-text">{liveText}</div>
      </div>

      <div id="summary-section">
        <div className="label">Last summary</div>
        <div id="summary-text">{summaryText}</div>
      </div>

      {questionVisible && (
        <div id="question-section" className="visible">
          <div className="label">Someone's asking you</div>
          <div id="transcript-text">"{question.transcript}"</div>
          <div className="label" style={{ marginBottom: "6px" }}>
            Suggested response
          </div>
          <div id="answer-text">{question.answer}</div>
          <button onClick={dismiss}>Dismiss</button>
        </div>
      )}
    </div>
  );
}
