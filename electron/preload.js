'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('clipSearch', {
    onBackendStatus: (callback) => {
        const listener = (_event, payload) => callback(payload);
        ipcRenderer.on('backend-status', listener);
        return () => ipcRenderer.removeListener('backend-status', listener);
    },
});
