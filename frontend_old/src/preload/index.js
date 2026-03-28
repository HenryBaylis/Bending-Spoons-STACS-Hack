import { contextBridge } from "electron";
import { electronAPI } from "@electron-toolkit/preload";

/*
const { ipcRenderer } = require("electron");

// ── DOM-based live updates (elements always present in MockWindow) ──
ipcRenderer.on("transcript", (_, data) => {
  const el = document.getElementById("live-text");
  if (el) el.textContent = data.text;
  if (Date.now() < (window._mentionActiveUntil || 0)) {
    const mel = document.getElementById("mention-text");
    if (mel) mel.textContent = data.words || data.text;
  }
});

ipcRenderer.on("summary", (_, data) => {
  const el = document.getElementById("summary-text");
  if (el) el.textContent = data.text;
});

ipcRenderer.on("mention", (_, data) => {
  const card = document.getElementById("card");
  if (card) {
    card.classList.remove("mentioned");
    void card.offsetWidth;
    card.classList.add("mentioned");
    setTimeout(() => card.classList.remove("mentioned"), 1000);
  }
  window._mentionActiveUntil = Date.now() + 5000;
  const section = document.getElementById("mention-section");
  const text = document.getElementById("mention-text");
  if (section && text) {
    text.textContent = data.words || "";
    section.style.display = "block";
    setTimeout(() => {
      if (Date.now() >= window._mentionActiveUntil) {
        section.style.display = "none";
      }
    }, 5000);
  }
});

// ── React state callbacks ──
const api = {
  closeWindow: () => ipcRenderer.send("close-window"),
  startMeeting: (profile) => ipcRenderer.send("start-meeting", profile),
  resizeWindow: (height) => ipcRenderer.send("resize-window", height),
  dismiss: () => ipcRenderer.send("dismiss"),
  onQuestion: (cb) => ipcRenderer.on("question", (_, data) => cb(data)),
  onDismiss: (cb) => ipcRenderer.on("dismiss", () => cb()),
  onStopMeeting: (cb) => ipcRenderer.on("stop-meeting", () => cb()),
};

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
