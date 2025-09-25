
# Scans Storage containers and enqueues messages for the processor to handle.
import os, json, base64
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient

CONN = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
ENTRY_CONTAINER = os.environ.get("ENTRY_CONTAINER","images-entry")
EXIT_CONTAINER = os.environ.get("EXIT_CONTAINER","images-exit")
QUEUE = os.environ.get("QUEUE_NAME","ingest")

def enqueue_for_container(container_name):
    bs = BlobServiceClient.from_connection_string(CONN)
    qc = QueueClient.from_connection_string(CONN, QUEUE)
    cont = bs.get_container_client(container_name)
    for blob in cont.list_blobs():
        payload = {"container": container_name, "name": blob.name, "cameraId": "cam1"}
        msg = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
        qc.send_message(msg)
        print("Enqueued:", payload)

if __name__ == "__main__":
    enqueue_for_container(ENTRY_CONTAINER)
    enqueue_for_container(EXIT_CONTAINER)
    print("Done.")
