import Versions from "./components/Versions";
import electronLogo from "./assets/electron.svg";

function App() {
  const ipcHandle = () => window.electron.ipcRenderer.send("ping");

  return (
    <>
      <div className="actions">
        <div className="action">
          <a target="_blank" rel="noreferrer" onClick={ipcHandle}>
            Send IPC
          </a>
        </div>
      </div>
    </>
  );
}

export default App;
