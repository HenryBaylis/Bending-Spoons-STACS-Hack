const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')

let win

function createWindow() {
  win = new BrowserWindow({
    width: 420,
    height: 180,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  })

  win.loadFile('index.html')
  win.setIgnoreMouseEvents(false)

  // Position bottom-right
  const { screen } = require('electron')
  const { width, height } = screen.getPrimaryDisplay().workAreaSize
  win.setPosition(width - 440, height - 200)
}

app.whenReady().then(() => {
  createWindow()

  // Simulate a meeting question arriving after 3 seconds
  setTimeout(() => {
    win.webContents.send('question', {
      transcript: 'Henry, what is the current status of the auth migration?',
      answer: 'We\'re about 70% through — OAuth2 endpoints are live, we\'re migrating legacy sessions this sprint and targeting completion by end of Q3.'
    })
  }, 3000)

  // Simulate a second question after 8 seconds
  setTimeout(() => {
    win.webContents.send('question', {
      transcript: 'Can you give us a risk assessment on the timeline?',
      answer: 'Main risk is the legacy session volume — we\'re running parallel systems for two weeks as a safety net, so slippage would be a two-week delay at most.'
    })
  }, 8000)
})

ipcMain.on('dismiss', () => {
  win.webContents.send('dismiss')
})

app.on('window-all-closed', () => app.quit())
