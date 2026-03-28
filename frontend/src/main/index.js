import { app, shell, BrowserWindow, ipcMain, screen } from "electron";
import { join } from "path";
import { spawn } from "child_process";
import { existsSync, writeFileSync } from "fs";
import { electronApp, optimizer, is } from "@electron-toolkit/utils";
import icon from "../../resources/icon.png?asset";

let win;
let python;

function createWindow() {
  win = new BrowserWindow({
    width: 420,
    height: 260,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === "linux" ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      nodeIntegration: true,
      contextIsolation: false,
      sandbox: false,
    },
  });

  win.on("ready-to-show", () => {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;
    win.setPosition(width - 440, height - 300);
    win.show();
  });

  win.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: "deny" };
  });

  if (is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    win.loadURL(process.env["ELECTRON_RENDERER_URL"]);
  } else {
    win.loadFile(join(__dirname, "../renderer/index.html"));
  }
}

function spawnPython() {
  const venvPython = join(__dirname, "../../../backend/.venv/bin/python");
  const pythonBin = existsSync(venvPython) ? venvPython : "python";
  python = spawn(pythonBin, [join(__dirname, "../../../backend/main.py")], {
    cwd: join(__dirname, "../../../backend"),
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

app.whenReady().then(() => {
  electronApp.setAppUserModelId("com.electron");

  app.on("browser-window-created", (_, window) => {
    optimizer.watchWindowShortcuts(window);
  });

  createWindow();

  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

ipcMain.on("start-meeting", (_, profile) => {
  const profilePath = join(__dirname, "../../../backend/profile.json");
  writeFileSync(profilePath, JSON.stringify(profile, null, 2));
  win.setIgnoreMouseEvents(true, { forward: true });
  spawnPython();
});

ipcMain.on("resize-window", (_, height) => {
  win.setContentSize(420, height);
});

ipcMain.on("dismiss", () => {
  win.setIgnoreMouseEvents(true, { forward: true });
  win.webContents.send("dismiss");
});

ipcMain.on("close-window", () => {
  if (python) python.kill();
  app.quit();
});

app.on("window-all-closed", () => {
  if (python) python.kill();
  app.quit();
});
