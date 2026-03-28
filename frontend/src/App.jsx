import { useState, useEffect, useRef } from "react";
import FillForm from "./components/FillForm";
import MockWindow from "./components/MockWindow";
import ExpandedWindow from "./components/ExpandedWindow";
import ModeSelector from "./components/ModeSelector";

export default function App() {
  const [stage, setStage] = useState("form"); // 'form' | 'mock' | 'expanded'
  const [modes, setModes] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [followUp, setFollowUp] = useState(null);
  const containerRef = useRef(null);

  const handleClose = () => window.api?.closeWindow();

  useEffect(() => {
    if (stage === "form") return;
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver(() => {
      window.api?.resizeWindow(el.offsetHeight);
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [stage]);

  useEffect(() => {
    window.api?.onQuestion((data) => {
      setQuestion(data.transcript);
      setAnswer(data.answer);
      setFollowUp(data.follow_up || null);
      setStage("expanded");
    });
    window.api?.onDismiss(() => setStage("mock"));
    window.api?.onStopMeeting(() => setStage("form"));
  }, []);

  const handleStart = (profile) => {
    window.api.startMeeting(profile);
    setStage("mock");
  };

  return (
    <div id="card" style={{ position: "relative" }} ref={containerRef}>
      <button onClick={handleClose} style={{ position: "absolute", top: 4, right: 4 }}>✕</button>
      {stage === "form" && (
        <FillForm onSubmit={handleStart} />
      )}
      {stage !== "form" && (
        <MockWindow modeSelector={<ModeSelector modes={modes} onChange={setModes} />}>
          {stage === "expanded" && (
            <ExpandedWindow
              question={question}
              answer={answer}
              followUp={followUp}
              modes={modes}
              onDismiss={() => {
                setStage("mock");
                window.api?.dismiss();
              }}
            />
          )}
        </MockWindow>
      )}
    </div>
  );
}
