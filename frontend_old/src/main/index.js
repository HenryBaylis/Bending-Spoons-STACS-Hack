import { app, shell, BrowserWindow, ipcMain } from "electron";
import { join } from "path";
import { electronApp, optimizer, is } from "@electron-toolkit/utils";
import icon from "../../resources/icon.png?asset";

function createWindow() {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
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

  mainWindow.on("ready-to-show", () => {
    mainWindow.show();
  });

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: "deny" };
  });

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    mainWindow.loadURL(process.env["ELECTRON_RENDERER_URL"]);
  } else {
    mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
  }

  //mainWindow.setIgnoreMouseEvents(true, { forward: true });
}

/*
function spawnPython() {
  const venvPython = path.join(__dirname, "../backend/.venv/bin/python");
  const systemPython = "python";
  const pythonBin = require("fs").existsSync(venvPython)
    ? venvPython
    : systemPython;
  python = spawn(pythonBin, [path.join(__dirname, "../backend/main.py")], {
    cwd: path.join(__dirname, "../backend"),
  });

  let buffer = "";
  python.stdout.on("data", (data) => {
    buffer += data.toString();
    const lines = buffer.split("\n");
    buffer = lines.pop(); // keep incomplete line
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
*/

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId("com.electron");

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on("browser-window-created", (_, window) => {
    optimizer.watchWindowShortcuts(window);
  });

  // IPC test
  ipcMain.on("ping", () => console.log("pong"));

  createWindow();
  //spawnPython();

  app.on("activate", function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

ipcMain.on("dismiss", () => {
  win.setIgnoreMouseEvents(true, { forward: true });
  win.webContents.send("dismiss");
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    //if (python) python.kill();
    app.quit();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
