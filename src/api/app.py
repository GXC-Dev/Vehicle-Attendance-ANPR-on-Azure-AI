
import os
from fastapi import FastAPI
from azure.data.tables import TableServiceClient

TABLE = os.environ.get("TABLE_NAME","events")
CONN = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")

app = FastAPI(title="Vehicle Attendance API")

@app.get("/healthz")
def health():
    return {"ok": True}

@app.get("/api/events")
def list_events(date: str = None, top: int = 100):
    ts = TableServiceClient.from_connection_string(CONN)
    tc = ts.get_table_client(TABLE)
    if not date:
        # get today's date in UTC
        from datetime import datetime, timezone
        date = datetime.now(timezone.utc).date().isoformat()
    pk = date
    entities = tc.query_entities(f"PartitionKey eq '{pk}'", results_per_page=top)
    out = []
    for e in entities:
        out.append({
            "id": e.get("RowKey"),
            "ts": e.get("ts"),
            "plate": e.get("plate"),
            "type": e.get("type"),
            "confidence": e.get("confidence"),
            "cameraId": e.get("cameraId"),
            "container": e.get("container"),
            "blobName": e.get("blobName")
        })
        if len(out) >= top:
            break
    return {"items": out}
