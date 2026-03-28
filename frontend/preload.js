const { ipcRenderer } = require('electron')

window.api = {
  startMeeting: (profile) => ipcRenderer.send('start-meeting', profile),
  dismiss: () => ipcRenderer.send('dismiss'),
  resizeWindow: (height) => ipcRenderer.send('resize-window', height),
  closeWindow: () => ipcRenderer.send('close-window'),
  onQuestion: (cb) => ipcRenderer.on('question', (_, data) => cb(data)),
  onDismiss: (cb) => ipcRenderer.on('dismiss', (_, data) => cb(data)),
  onStopMeeting: (cb) => ipcRenderer.on('stop-meeting', (_, data) => cb(data)),
}
