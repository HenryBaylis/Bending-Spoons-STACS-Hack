"use strict";
const electron = require("electron");
const preload = require("@electron-toolkit/preload");
const { ipcRenderer } = require("electron");
ipcRenderer.on("transcript", (_, data) => {
  document.getElementById("live-text").textContent = data.text;
});
ipcRenderer.on("summary", (_, data) => {
  document.getElementById("summary-text").textContent = data.text;
});
ipcRenderer.on("question", (_, data) => {
  document.getElementById("transcript-text").textContent = `"${data.transcript}"`;
  document.getElementById("answer-text").textContent = data.answer;
  document.getElementById("question-section").classList.add("visible");
});
ipcRenderer.on("dismiss", () => {
  document.getElementById("question-section").classList.remove("visible");
});
const api = {};
if (process.contextIsolated) {
  try {
    electron.contextBridge.exposeInMainWorld("electron", preload.electronAPI);
    electron.contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  window.electron = preload.electronAPI;
  window.api = api;
}
