"use strict";
const electron = require("electron");
const path = require("path");
const child_process = require("child_process");
const fs = require("fs");
const utils = require("@electron-toolkit/utils");
const icon = path.join(__dirname, "../../resources/icon.png");
let win;
let python;
function createWindow() {
  win = new electron.BrowserWindow({
    width: 420,
    height: 260,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    show: false,
    autoHideMenuBar: true,
    ...process.platform === "linux" ? { icon } : {},
    webPreferences: {
      preload: path.join(__dirname, "../preload/index.js"),
      nodeIntegration: true,
      contextIsolation: false,
      sandbox: false
    }
  });
  win.on("ready-to-show", () => {
    const { width, height } = electron.screen.getPrimaryDisplay().workAreaSize;
    win.setPosition(width - 440, height - 300);
    win.show();
  });
  win.webContents.setWindowOpenHandler((details) => {
    electron.shell.openExternal(details.url);
    return { action: "deny" };
  });
  if (utils.is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    win.loadURL(process.env["ELECTRON_RENDERER_URL"]);
  } else {
    win.loadFile(path.join(__dirname, "../renderer/index.html"));
  }
}
function spawnPython() {
  const venvPython = path.join(__dirname, "../../../backend/.venv/bin/python");
  const pythonBin = fs.existsSync(venvPython) ? venvPython : "python";
  python = child_process.spawn(pythonBin, [path.join(__dirname, "../../../backend/main.py")], {
    cwd: path.join(__dirname, "../../../backend")
  });
  let buffer = "";
  python.stdout.on("data", (data) => {
    buffer += data.toString();
    const lines = buffer.split("\n");
    buffer = lines.pop();
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const event = JSON.parse(line);
        if (event.type === "transcript" || event.type === "summary") {
          win.webContents.send(event.type, event);
        } else if (event.type === "question") {
          win.setIgnoreMouseEvents(false);
          win.webContents.send("question", event);
        }
      } catch (e) {
        console.error("Failed to parse Python event:", line);
      }
    }
  });
  python.stderr.on("data", (data) => {
    console.error("[python]", data.toString());
  });
  python.on("exit", (code) => {
    console.log(`Python exited with code ${code}`);
  });
}
electron.app.whenReady().then(() => {
  utils.electronApp.setAppUserModelId("com.electron");
  electron.app.on("browser-window-created", (_, window) => {
    utils.optimizer.watchWindowShortcuts(window);
  });
  createWindow();
  electron.app.on("activate", function() {
    if (electron.BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});
electron.ipcMain.on("start-meeting", (_, profile) => {
  const profilePath = path.join(__dirname, "../../../backend/profile.json");
  fs.writeFileSync(profilePath, JSON.stringify(profile, null, 2));
  win.setIgnoreMouseEvents(true, { forward: true });
  spawnPython();
});
electron.ipcMain.on("resize-window", (_, height) => {
  win.setContentSize(420, height);
});
electron.ipcMain.on("dismiss", () => {
  win.setIgnoreMouseEvents(true, { forward: true });
  win.webContents.send("dismiss");
});
electron.ipcMain.on("close-window", () => {
  if (python) python.kill();
  electron.app.quit();
});
electron.app.on("window-all-closed", () => {
  if (python) python.kill();
  electron.app.quit();
});
