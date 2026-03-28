import { app, shell, BrowserWindow, ipcMain, screen, globalShortcut } from "electron";
import { join, extname } from "path";
import { spawn } from "child_process";
import { existsSync, writeFileSync, unlinkSync } from "fs";
import { electronApp, optimizer, is } from "@electron-toolkit/utils";
import icon from "../../resources/icon.png?asset";

let win;
let python;
let contextFilePath = null;

function createWindow() {
  win = new BrowserWindow({
    width: 420,
    height: 360,
    transparent: true,
    // DOESNT WORK FOR SOME REASON
    //frame: false,
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

function spawnPython(env = {}) {
  const venvPython = join(__dirname, "../../../backend/.venv/bin/python");
  const pythonBin = existsSync(venvPython) ? venvPython : "python";
  python = spawn(pythonBin, [join(__dirname, "../../../backend/main.py")], {
    cwd: join(__dirname, "../../../backend"),
    env: { ...process.env, ...env },
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
        } else if (event.type === "mention") {
          win.webContents.send("mention", event);
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

  globalShortcut.register("CommandOrControl+Shift+M", () => {
    if (python) {
      python.kill();
      python = null;
    }
    if (contextFilePath && existsSync(contextFilePath)) {
      unlinkSync(contextFilePath);
      contextFilePath = null;
    }
    win.setIgnoreMouseEvents(false);
    win.webContents.send("stop-meeting");
  });

  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

ipcMain.on("start-meeting", (_, profile) => {
  const profilePath = join(__dirname, "../../../backend/profile.json");
  writeFileSync(profilePath, JSON.stringify({
    name: profile.name,
    job_title: profile.role,
    company: "",
    team: "",
    responsibilities: "",
    current_projects: "",
    extra_context: "",
  }, null, 2));

  const env = {};
  if (profile.contextFile) {
    const ext = extname(profile.contextFile).toLowerCase();
    env.MEETING_CONTEXT_PATH = profile.contextFile;
    env.MEETING_CONTEXT_TYPE = ext === ".pdf" ? "pdf" : "text";
    contextFilePath = profile.contextFile;
  }

  win.setIgnoreMouseEvents(true, { forward: true });
  spawnPython(env);
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

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});

app.on("window-all-closed", () => {
  if (python) python.kill();
  app.quit();
});
