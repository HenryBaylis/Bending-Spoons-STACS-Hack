import { useState, useEffect, useRef } from "react";
import FillForm from "./components/FillForm";
import MockWindow from "./components/MockWindow";
import ExpandedWindow from "./components/ExpandedWindow";

export default function App() {
  const [stage, setStage] = useState("form"); // 'form' | 'mock' | 'expanded'
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

  if (stage === "form") {
    return (
      <div ref={containerRef}>
        <FillForm onSubmit={handleStart} onClose={handleClose} />
      </div>
    );
  }

  return (
    <div ref={containerRef}>
      <MockWindow onClose={handleClose}>
        {stage === "expanded" && (
          <ExpandedWindow
            question={question}
            answer={answer}
            followUp={followUp}
            onDismiss={() => {
              setStage("mock");
              window.api?.dismiss();
            }}
          />
        )}
      </MockWindow>
    </div>
  );
}
