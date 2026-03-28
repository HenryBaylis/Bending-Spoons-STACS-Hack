import { contextBridge } from "electron";
import { electronAPI } from "@electron-toolkit/preload";

const { ipcRenderer } = require("electron");

ipcRenderer.on("transcript", (_, data) => {
  document.getElementById("live-text").textContent = data.text;
});

ipcRenderer.on("summary", (_, data) => {
  document.getElementById("summary-text").textContent = data.text;
});

ipcRenderer.on("question", (_, data) => {
  document.getElementById("transcript-text").textContent =
    `"${data.transcript}"`;
  document.getElementById("answer-text").textContent = data.answer;
  document.getElementById("question-section").classList.add("visible");
});

ipcRenderer.on("dismiss", () => {
  document.getElementById("question-section").classList.remove("visible");
});

function dismiss() {
  document.getElementById("question-section").classList.remove("visible");
  ipcRenderer.send("dismiss");
}

// Custom APIs for renderer
const api = {
  closeWindow: () => ipcRenderer.send("close-window"),
  startMeeting: (profile) => ipcRenderer.send("start-meeting", profile),
  resizeWindow: (height) => ipcRenderer.send("resize-window", height),
};

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld("electron", electronAPI);
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  window.electron = electronAPI;
  window.api = api;
}
