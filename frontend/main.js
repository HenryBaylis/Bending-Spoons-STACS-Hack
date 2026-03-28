const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let win
let python

function createWindow() {
  win = new BrowserWindow({
    width: 420,
    height: 260,
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

  win.loadFile(path.join(__dirname, 'index.html'))
  win.setIgnoreMouseEvents(true, { forward: true })

  const { screen } = require('electron')
  const { width, height } = screen.getPrimaryDisplay().workAreaSize
  win.setPosition(width - 440, height - 200)
}

function spawnPython() {
  const venvPython = path.join(__dirname, '../backend/.venv/bin/python')
  const systemPython = 'python'
  const pythonBin = require('fs').existsSync(venvPython) ? venvPython : systemPython
  python = spawn(pythonBin, [path.join(__dirname, '../backend/main.py')], {
    cwd: path.join(__dirname, '../backend')
  })

  let buffer = ''
  python.stdout.on('data', (data) => {
    buffer += data.toString()
    const lines = buffer.split('\n')
    buffer = lines.pop() // keep incomplete line
    for (const line of lines) {
      if (!line.trim()) continue
      try {
        const event = JSON.parse(line)
        if (event.type === 'transcript' || event.type === 'summary') {
          win.webContents.send(event.type, event)
        } else if (event.type === 'question') {
          win.setIgnoreMouseEvents(false)
          win.webContents.send('question', event)
        }
      } catch (e) {
        console.error('Failed to parse Python event:', line)
      }
    }
  })

  python.stderr.on('data', (data) => {
    console.error('[python]', data.toString())
  })

  python.on('exit', (code) => {
    console.log(`Python exited with code ${code}`)
  })
}

app.whenReady().then(() => {
  createWindow()
  spawnPython()
})

ipcMain.on('dismiss', () => {
  win.setIgnoreMouseEvents(true, { forward: true })
  win.webContents.send('dismiss')
})

app.on('window-all-closed', () => {
  if (python) python.kill()
  app.quit()
})
