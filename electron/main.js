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
const APP_ROOT = path.dirname(__dirname);

// In dev we run `python server.py` from the inference/ venv directly.
// In packaged builds the bundled FastAPI is next to clip-search.exe and
// exposes itself via the `clip-search-backend` binary name.
const BACKEND_CMD = isDev
    ? path.join(APP_ROOT, 'inference', '.venv', 'bin', 'python')
    : path.join(process.resourcesPath, 'app', 'clip-search-backend');

const BACKEND_ARGS_DEV = [
    path.join(APP_ROOT, 'inference', 'server.py'),
];

const BACKEND_CWD = isDev
    ? path.join(APP_ROOT, 'inference')
    : path.join(process.resourcesPath, 'app');

const BACKEND_HOST = '127.0.0.1';
const BACKEND_PORT = Number.parseInt(process.env.CLIP_SEARCH_PORT || '9000', 10);

// Time we wait for the FastAPI server to become reachable. Generous on first
// run when the model has to load from disk.
const STARTUP_TIMEOUT_MS = 60_000;
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
        PYTHONIOENCODING: 'utf-8',
    };

    console.log(`[clip-search] spawning backend: ${BACKEND_CMD} ${args.join(' ')}`);
    backendProcess = spawn(BACKEND_CMD, args, {
        cwd: BACKEND_CWD,
        env,
        stdio: ['ignore', 'pipe', 'pipe'],
        windowsHide: true,
    });

    backendProcess.stdout.on('data', (chunk) => {
        process.stdout.write(`[backend] ${chunk}`);
    });
    backendProcess.stderr.on('data', (chunk) => {
        process.stderr.write(`[backend] ${chunk}`);
    });
    backendProcess.on('exit', (code, signal) => {
        console.log(`[clip-search] backend exited code=${code} signal=${signal}`);
        backendProcess = null;
        if (mainWindow && !mainWindow.isDestroyed()) {
            mainWindow.webContents.send('backend-status', { running: false, code, signal });
        }
    });
    backendProcess.on('error', (err) => {
        console.error('[clip-search] failed to spawn backend:', err);
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
            mainWindow.webContents.executeJavaScript(
                `document.body && (document.body.innerHTML = ${JSON.stringify(
                    `<pre style="color:#fff;background:#7a1f1f;padding:24px;font-family:monospace">` +
                    `Backend failed to start.\\n\\n${err.message}\\n\\nCheck that data/search_index/ exists next to clip-search.exe.</pre>`,
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
