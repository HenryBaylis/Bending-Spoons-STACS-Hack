const { app, BrowserWindow, ipcMain, globalShortcut, screen } = require('electron')
const path = require('path')
const fs = require('fs')
const { spawn } = require('child_process')

let win
let python
let contextFilePath = null

function createWindow() {
  win = new BrowserWindow({
    width: 480,
    height: 520,
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
  win.center()
}

function spawnPython(env = {}) {
  const venvPython = path.join(__dirname, '../backend/.venv/bin/python')
  const pythonBin = fs.existsSync(venvPython) ? venvPython : 'python'

  python = spawn(pythonBin, [path.join(__dirname, '../backend/main.py')], {
    cwd: path.join(__dirname, '../backend'),
    env: { ...process.env, ...env }
  })

  let buffer = ''
  python.stdout.on('data', (data) => {
    buffer += data.toString()
    const lines = buffer.split('\n')
    buffer = lines.pop()
    for (const line of lines) {
      if (!line.trim()) continue
      try {
        const event = JSON.parse(line)
        if (event.type === 'mention') {
          win.webContents.send('mention', event)
        } else if (event.type === 'transcript' || event.type === 'summary') {
          win.webContents.send(event.type, event)
        } else if (event.type === 'question') {
          win.webContents.send('question', event)
        } else if (event.type === 'commitment') {
          win.webContents.send('commitment', event)
        } else if (event.type === 'tactic') {
          win.webContents.send('tactic', event)
        } else if (event.type === 'assertiveness') {
          win.webContents.send('assertiveness', event)
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

function startMeeting(payload) {
  // Write profile.json
  const profile = {
    name: payload.name,
    job_title: payload.jobTitle,
    company: '',
    team: '',
    responsibilities: '',
    current_projects: '',
    extra_context: ''
  }
  fs.writeFileSync(
    path.join(__dirname, '../backend/profile.json'),
    JSON.stringify(profile, null, 2)
  )

  // Write context file if provided
  const env = {}
  if (payload.contextFile) {
    const ext = path.extname(payload.contextFile.name).toLowerCase()
    const dest = path.join(__dirname, `../backend/meeting_context${ext}`)
    if (payload.contextFile.type === 'application/pdf') {
      fs.writeFileSync(dest, Buffer.from(payload.contextFile.data))
      env.MEETING_CONTEXT_PATH = dest
      env.MEETING_CONTEXT_TYPE = 'pdf'
    } else {
      fs.writeFileSync(dest, payload.contextFile.data, 'utf8')
      env.MEETING_CONTEXT_PATH = dest
      env.MEETING_CONTEXT_TYPE = 'text'
    }
    contextFilePath = dest
  }

  spawnPython(env)

  // Switch to overlay mode
  const { width, height } = screen.getPrimaryDisplay().workAreaSize
  win.setSize(840, 260)
  win.setPosition(width - 860, height - 200)
  win.webContents.send('show-overlay')
}

function stopMeeting() {
  if (!python) return
  python.kill()
  python = null

  if (contextFilePath && fs.existsSync(contextFilePath)) {
    fs.unlinkSync(contextFilePath)
    contextFilePath = null
  }

  win.setSize(480, 520)
  win.center()
  win.setIgnoreMouseEvents(false)
  win.webContents.send('show-setup')
}

app.whenReady().then(() => {
  createWindow()

  win.webContents.once('did-finish-load', () => {
    win.webContents.send('show-setup')
  })

  globalShortcut.register('CommandOrControl+Shift+M', stopMeeting)
})

ipcMain.on('start-meeting', (_, payload) => {
  startMeeting(payload)
})

ipcMain.on('dismiss', () => {
  win.webContents.send('dismiss')
})

ipcMain.on('analyse-tactics', () => {
  if (python) python.stdin.write('analyse-tactics\n')
})

ipcMain.on('trigger-assertiveness', () => {
  if (python) python.stdin.write('trigger-assertiveness\n')
})

ipcMain.on('set-ignore-mouse', (_, ignore) => {
  win.setIgnoreMouseEvents(ignore, { forward: true })
})

app.on('will-quit', () => {
  globalShortcut.unregisterAll()
})

app.on('window-all-closed', () => {
  if (python) python.kill()
  app.quit()
})
