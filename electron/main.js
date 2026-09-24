'use strict';

const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const isDev = !app.isPackaged;

// APP_ROOT points at the directory that contains the running exe. In dev
// that's the repo root (electron/ is one level deep), in packaged builds
// it's the folder where the user placed clip-search-0.1.0-portable.exe.
//
// For *portable* Electron builds the exe extracts itself into %TEMP% at
// launch, so process.execPath would resolve to that scratch directory and
// `data/` next to the user-facing exe would be invisible. Electron exposes
// PORTABLE_EXECUTABLE_DIR specifically for that case — it points back at
// the real folder the user clicked from. We prefer it whenever it is set.
const APP_ROOT = isDev
    ? path.dirname(__dirname)
    : (process.env.PORTABLE_EXECUTABLE_DIR || path.dirname(process.execPath));

// In dev we run `python server.py` from the inference/ venv directly.
// In packaged builds the bundled FastAPI lives at:
//   <resources>/app/clip-search-backend/clip-search-backend.exe
// PyInstaller --onedir places the actual exe inside the bundle folder, not
// at the bundle root, so we have to point at the .exe (with platform suffix).
const BACKEND_BIN = process.platform === 'win32'
    ? 'clip-search-backend.exe'
    : 'clip-search-backend';

const BACKEND_CMD = isDev
    ? path.join(APP_ROOT, 'inference', '.venv', 'bin', 'python')
    : path.join(process.resourcesPath, 'app', 'clip-search-backend', BACKEND_BIN);

const BACKEND_ARGS_DEV = [
    path.join(APP_ROOT, 'inference', 'server.py'),
];

// PyInstaller --onedir needs the cwd to be the bundle folder so the
// bundled exe can find its sibling _internal/ directory.
const BACKEND_CWD = isDev
    ? path.join(APP_ROOT, 'inference')
    : path.join(process.resourcesPath, 'app', 'clip-search-backend');

const BACKEND_HOST = '127.0.0.1';
const BACKEND_PORT = Number.parseInt(process.env.CLIP_SEARCH_PORT || '9000', 10);

// Time we wait for the FastAPI server to become reachable. Generous on first
// run when the model has to load from disk.
const STARTUP_TIMEOUT_MS = 90_000;
const STARTUP_POLL_MS = 500;

let backendProcess = null;
let mainWindow = null;
let backendPort = BACKEND_PORT;

// ---------------------------------------------------------------------------
// Backend lifecycle
// ---------------------------------------------------------------------------

function spawnBackend() {
    const args = isDev
        ? BACKEND_ARGS_DEV
        : [];
    const env = {
        ...process.env,
        HOST: BACKEND_HOST,
        PORT: String(backendPort),
        DATA_ROOT: process.env.DATA_ROOT || path.join(APP_ROOT, 'data'),
        INDEX_ROOT: process.env.INDEX_ROOT || path.join(APP_ROOT, 'data', 'search_index'),
        FRONTEND_DIST: process.env.FRONTEND_DIST || path.join(process.resourcesPath, 'app', 'frontend'),
        PYTHONIOENCODING: 'utf-8',
    };

    console.log(`[clip-search] spawning backend: ${BACKEND_CMD} ${args.join(' ')}`);
    console.log(`[clip-search] cwd: ${BACKEND_CWD}`);
    console.log(`[clip-search] DATA_ROOT: ${env.DATA_ROOT}`);
    console.log(`[clip-search] FRONTEND_DIST: ${env.FRONTEND_DIST}`);

    backendProcess = spawn(BACKEND_CMD, args, {
        cwd: BACKEND_CWD,
        env,
        stdio: ['ignore', 'pipe', 'pipe'],
        windowsHide: true,
    });

    // Also tee backend stderr into a log file next to the exe so users can
    // inspect failures even when the Electron window is gone.
    let logStream = null;
    if (!isDev) {
        try {
            logStream = fs.createWriteStream(
                path.join(APP_ROOT, 'clip-search-backend.log'),
                { flags: 'a' },
            );
        } catch (logErr) {
            console.error('[clip-search] cannot open backend log file:', logErr.message);
        }
    }

    backendProcess.stdout.on('data', (chunk) => {
        process.stdout.write(`[backend] ${chunk}`);
        if (logStream) {
            logStream.write(`[stdout] ${chunk}`);
        }
    });
    backendProcess.stderr.on('data', (chunk) => {
        process.stderr.write(`[backend] ${chunk}`);
        if (logStream) {
            logStream.write(`[stderr] ${chunk}`);
        }
    });
    backendProcess.on('exit', (code, signal) => {
        console.log(`[clip-search] backend exited code=${code} signal=${signal}`);
        if (logStream) {
            logStream.end(`[exit] code=${code} signal=${signal}\n`);
        }
        backendProcess = null;
        if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('backend-status', { running: false, code, signal });
        }
    });
    backendProcess.on('error', (err) => {
        console.error('[clip-search] failed to spawn backend:', err.message);
        if (logStream) {
            logStream.write(`[error] ${err.message}\n`);
        }
    });
}

function waitForBackend(timeoutMs) {
    const deadline = Date.now() + timeoutMs;
    return new Promise((resolve, reject) => {
        const probe = () => {
            const req = http.request({
                host: BACKEND_HOST,
                port: backendPort,
                path: '/health',
                method: 'GET',
                timeout: 1000,
            }, (res) => {
                if (res.statusCode === 200) {
                    res.resume();
                    return resolve();
                }
                res.resume();
                retry();
            });
            req.on('error', retry);
            req.on('timeout', () => {
                req.destroy();
                retry();
            });
            req.end();

            function retry() {
                if (Date.now() > deadline) {
                    return reject(new Error(`Backend did not become ready within ${timeoutMs}ms`));
                }
                setTimeout(probe, STARTUP_POLL_MS);
            }
        };
        probe();
    });
}

// ---------------------------------------------------------------------------
// Window
// ---------------------------------------------------------------------------

function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 820,
        minWidth: 960,
        minHeight: 640,
        title: 'AIC Clip Search',
        backgroundColor: '#0b1220',
        show: false,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: false,
        },
    });

    mainWindow.removeMenu();
    mainWindow.once('ready-to-show', () => mainWindow.show());

    // Open external links in the user's browser, never inside the app.
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        if (url.startsWith('http')) {
            shell.openExternal(url);
        }
        return { action: 'deny' };
    });

    const target = `http://${BACKEND_HOST}:${backendPort}/`;
    console.log(`[clip-search] loading ${target}`);
    mainWindow.loadURL(target).catch((err) => {
        console.error('[clip-search] loadURL failed:', err);
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------

app.whenReady().then(async () => {
    spawnBackend();
    try {
        await waitForBackend(STARTUP_TIMEOUT_MS);
        console.log('[clip-search] backend is ready');
    } catch (err) {
        console.error('[clip-search] backend startup failed:', err.message);
        if (mainWindow === null) {
            createMainWindow();
        }
        if (mainWindow) {
            const logPath = path.join(APP_ROOT, 'clip-search-backend.log');
            mainWindow.webContents.executeJavaScript(
                `document.body && (document.body.innerHTML = ${JSON.stringify(
                    `<pre style="color:#fff;background:#7a1f1f;padding:24px;font-family:monospace;white-space:pre-wrap;word-break:break-word">` +
                    `Backend failed to start.\n\n${err.message}\n\n` +
                    `Details:\n` +
                    `  Backend exe: ${BACKEND_CMD}\n` +
                    `  CWD: ${BACKEND_CWD}\n` +
                    `  DATA_ROOT: ${process.env.DATA_ROOT || path.join(APP_ROOT, 'data')}\n\n` +
                    `Check:\n` +
                    `  1. clip-search-backend/ folder exists next to this exe\n` +
                    `  2. data/search_index/ exists next to this exe\n` +
                    `  3. Full stderr in: ${logPath}</pre>`,
                )})`,
            );
        }
        return;
    }
    createMainWindow();
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createMainWindow();
    }
});

app.on('before-quit', () => {
    if (backendProcess) {
        try {
            backendProcess.kill();
        } catch (_err) {
            // already dead
        }
    }
});

process.on('uncaughtException', (err) => {
    console.error('[clip-search] uncaughtException:', err);
});
