
import os, json, base64, datetime, traceback
from azure.storage.queue import QueueClient
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient

CONN = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
QUEUE = os.environ.get("QUEUE_NAME","ingest")
TABLE = os.environ.get("TABLE_NAME","events")
ENTRY_CONTAINER = os.environ.get("ENTRY_CONTAINER","images-entry")
EXIT_CONTAINER = os.environ.get("EXIT_CONTAINER","images-exit")
CONF_THRESHOLD = float(os.environ.get("CONF_THRESHOLD","0.85"))

from .ocr_read import ocr_plate

def get_clients():
    qc = QueueClient.from_connection_string(CONN, QUEUE)
    bs = BlobServiceClient.from_connection_string(CONN)
    ts = TableServiceClient.from_connection_string(CONN)
    try:
        tc = ts.create_table_if_not_exists(TABLE)
    except Exception:
        tc = ts.get_table_client(TABLE)
    return qc, bs, tc

def upsert_event(table_client, event):
    # Partition by date; RowKey as unique id
    pk = event["ts"][:10]  # yyyy-mm-dd
    rk = event["id"]
    entity = event.copy()
    entity["PartitionKey"] = pk
    entity["RowKey"] = rk
    table_client.upsert_entity(entity=entity, mode="Merge")

def process_message(table_client, blob_client, msg):
    # msg expected: {"container":"images-entry","name":"path/to/file.png","cameraId":"cam1"}
    container = msg["container"]
    name = msg["name"]
    cam = msg.get("cameraId","cam1")
    ev_type = "entry" if container == ENTRY_CONTAINER else ("exit" if container == EXIT_CONTAINER else "unknown")

    b = blob_client.get_blob_client(container, name).download_blob().readall()
    plate, conf = ocr_plate(name, b)
    now = datetime.datetime.utcnow().isoformat()

    event = {
        "id": f"{now}_{name.replace('/','_')}",
        "plate": plate or "UNKNOWN",
        "confidence": conf,
        "type": ev_type if conf >= CONF_THRESHOLD else "unknown",
        "cameraId": cam,
        "blobName": name,
        "container": container,
        "ts": now
    }
    upsert_event(table_client, event)
    return event

def main_loop():
    qc, bs, tc = get_clients()
    print("Processor started. Listening on queue:", QUEUE)
    while True:
        msgs = qc.receive_messages(messages_per_page=16, visibility_timeout=60)
        any_msg = False
        for m in msgs:
            any_msg = True
            try:
                payload = json.loads(base64.b64decode(m.content).decode('utf-8')) if m.content else {}
                ev = process_message(tc, bs, payload)
                print("Processed:", ev["plate"], ev["type"], ev["blobName"])
                qc.delete_message(m)
            except Exception as e:
                print("ERROR:", e)
                traceback.print_exc()
                # Abandon (visibility timeout will make it reappear)
        if not any_msg:
            import time; time.sleep(2)

if __name__ == "__main__":
    assert CONN, "AZURE_STORAGE_CONNECTION_STRING is required"
    main_loop()
