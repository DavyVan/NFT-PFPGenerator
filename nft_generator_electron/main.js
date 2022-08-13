'use strict';

const child_process = require("child_process");
const util = require("node:util");
const execFile = util.promisify(child_process.execFile);
const path = require("path");
const { app, BrowserWindow, ipcMain} = require("electron");
const remote_main = require("@electron/remote/main");
remote_main.initialize();

let nftgServerChildProcess = null;
let indexWin = null;
let pid = -1;

const run = () => {
    indexWin = new BrowserWindow({
        width: 800,
        height: 600,
        resizable: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        title: "NFT Generator | 2m.xyz"
    });
    indexWin.setMenu(null);
    indexWin.loadFile("app/index.html");
    indexWin.webContents.openDevTools({
        mode: "detach"
    });
    remote_main.enable(indexWin.webContents);
};

const run_server = async () => {
    nftgServerChildProcess = execFile(path.resolve(app.getAppPath() + "/app/bin/nftg_server.exe"), ["runserver", "23333", "--noreload"], (error) => {
        console.log("NFTG Server terminated.");
        if (error) {
            console.log(error);
        }
    }).child;
    console.log("NFTG Server started: " + nftgServerChildProcess.pid);
}

app.whenReady().then(() => {
    run();
    run_server();
});

app.on("before-quit", (event) => {
    if (pid != -1) {
        process.kill(pid, "SIGINT");
        console.log("NFTG Server Killed");
    }
});

ipcMain.handle("pid", (event, _pid) => {
    pid = _pid;
    console.log("main: get pid: %d", pid);
});