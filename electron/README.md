# AIC Clip Search (Electron)

Local desktop shell for the AIC CLIP search demo. Wraps the FastAPI backend
(`inference/server.py`) and the static Next.js frontend in a single
double-clickable Windows executable. No Python, Node, or Docker required on
the test machine.

## Layout

```
clip-search-portable.exe     (~280 MB; bundles backend + frontend)
data/                        (~7 GB; user copies separately)
├── search_index/
├── keyframes/
└── videos/
```

The exe expects `data/` as a sibling directory at runtime. If `data/` is
missing, the backend returns a clear error and the Electron window shows it.

## Build (Windows host)

```cmd
:: 1. Install Python deps for the inference server
cd inference
uv sync --extra export --extra build
cd ..

:: 2. Export ONNX + tokenizer into inference/models/
::    (Skipped if models/ already exists)
cd inference
.venv\Scripts\python.exe export_onnx.py
.venv\Scripts\python.exe download_tokenizer.py
cd ..

:: 3. Build the FastAPI backend exe
cd inference
.venv\Scripts\pyinstaller.exe --noconfirm --clean --onedir ^
  --name clip-search-backend ^
  --add-data "models/text_encoder.onnx;models" ^
  --add-data "models/text_encoder.onnx.data;models" ^
  --add-data "models/tokenizer;models/tokenizer" ^
  server.py
cd ..

:: 4. Build the frontend (static export so PyInstaller can serve it)
cd frontend
set NEXT_OUTPUT=export
npm ci
npm run build
cd ..

:: 5. Build the Electron wrapper
cd electron
npm ci
npm run build:win
```

Output: `electron/dist/clip-search-0.1.0-portable.exe`.

## Test machine workflow

1. Copy `clip-search-0.1.0-portable.exe` to the test machine.
2. Copy the repo's `data/` folder next to it.
3. Double-click the exe.
4. Window opens at `http://127.0.0.1:9000/` with the search UI.

## Why static export for the frontend

The Next.js `output: 'standalone'` mode requires a Node.js runtime, which
PyInstaller can't bundle. Switching to `output: 'export'` produces a
pure-HTML/CSS/JS bundle that FastAPI serves via `StaticFiles`.

The VPS deploy still uses `output: 'standalone'` (it has Node available);
the build picks the mode from `NEXT_OUTPUT` env var in `next.config.ts`.

## Limitations

- Search uses brute-force cosine on PCA-reduced (24-dim) vectors, no Annoy.
  This is fast enough for ~10k records but slower than the production
  indexer. Add `annoy>=1.17` to `inference/pyproject.toml` if scaling up.
- The CLIP ONNX model is fixed-batch=1 due to a known bug in the exporter.
  `_encode_texts()` falls back to per-text iteration, which is fine for
  `/api/search` (always single-query) but slower for `/embed` with many texts.
- 7 GB dataset must live next to the exe; the Electron app does not auto-
  download it (kept out of the binary to avoid 7 GB installers).
