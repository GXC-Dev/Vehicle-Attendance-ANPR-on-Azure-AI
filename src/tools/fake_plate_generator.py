
# Generates simple SVG "plate images" and uploads to Storage containers.
# Plates encoded in filenames so the demo processor can 'OCR' them.

import os, random, string, datetime
from azure.storage.blob import BlobServiceClient

ENTRY_CONTAINER = os.environ.get("ENTRY_CONTAINER","images-entry")
EXIT_CONTAINER = os.environ.get("EXIT_CONTAINER","images-exit")
ST_CONN = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

def rand_plate():
    # e.g., ABC123 or AB1234
    if random.random() < 0.5:
        return "".join(random.choices(string.ascii_uppercase, k=3)) + "".join(random.choices(string.digits, k=3))
    else:
        return "".join(random.choices(string.ascii_uppercase, k=2)) + "".join(random.choices(string.digits, k=4))

def svg_bytes(plate):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200">
<rect x="10" y="50" width="380" height="100" rx="8" ry="8" stroke="black" fill="white" stroke-width="4"/>
<text x="200" y="115" font-size="48" font-family="Arial" text-anchor="middle" fill="black">{plate}</text>
</svg>'''
    return svg.encode("utf-8")

def upload_sample(n=5):
    bs = BlobServiceClient.from_connection_string(ST_CONN)
    for i in range(n):
        plate = rand_plate()
        container = ENTRY_CONTAINER if i % 2 == 0 else EXIT_CONTAINER
        name = f"IMG_{plate}_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}_{i}.svg"
        bc = bs.get_blob_client(container, name)
        bc.upload_blob(svg_bytes(plate))
        print("Uploaded:", container, name)

if __name__ == "__main__":
    upload_sample(10)
