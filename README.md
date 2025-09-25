
# Vehicle Attendance (ANPR) on Azure
**Detects license plates from camera-dropped images and records entry/exit events** with timestamps. Includes sample data, a queue-driven processor, and a lightweight API for reporting.

## Features
- 📸 Ingestion: cameras drop images into **Blob Storage** (`images-entry` / `images-exit`)
- ⚙️ Processing: **Queue** → Python processor (detects plate from filename/OCR stub)
- 🗃️ Storage: events saved in **Azure Table Storage**
- 📈 API: list events by day for reporting/dashboards
- 🧪 Samples: fake plate generator + sample SVG images
- 🔐 Production-ready patterns listed (Event Grid, retries, alerts, privacy)

## Quick Start (Local)
1. Create resources with Bicep (or use existing).  
   ```powershell
   pwsh ./deploy/deploy.ps1
   ```
2. Put your `AZURE_STORAGE_CONNECTION_STRING` into `.env` or export as env var.
3. Generate & upload sample images to Storage:
   ```bash
   pip install -r src/tools/requirements.txt
   python src/tools/fake_plate_generator.py
   ```
4. Enqueue processing jobs:
   ```bash
   python src/tools/backfill.py
   ```
5. Start the processor (reads queue, writes events to Tables):
   ```bash
   pip install -r src/processor/requirements.txt
   python src/processor/main.py
   ```
6. Start the API:
   ```bash
   pip install -r src/api/requirements.txt
   uvicorn src.api.app:app --host 0.0.0.0 --port 8080
   ```
7. Test:
   - `GET http://localhost:8080/healthz`
   - `GET http://localhost:8080/api/events`

## Architecture (high level)
> _Replace with your diagram image later_
- **Blob Storage** (`images-entry`, `images-exit`)
- **Event Grid** (BlobCreated) → **Storage Queue** (`ingest`)
- **Processor** (container/Function) → OCR → **Table Storage (events)**
- **API** (FastAPI) → dashboards/Power BI

## Production notes
- Use **Event Grid** automatic wiring (Blob Created → Queue) for real cameras.
- Replace **OCR stub** with **Azure AI Vision Read** (confidence thresholds).
- Add **App Insights**, **retry policies**, **dead-letter** queue, and a **review UI**.
- Privacy: license plates may be PII; implement retention (e.g., 30–90 days).

## Repo Layout
```
deploy/        # bicep + deploy script
src/processor/ # queue listener + OCR stub
src/api/       # lightweight reporting API
src/tools/     # fake plate generator, backfill
tests/         # sample images + HTTP smoke tests
```

## License
MIT
