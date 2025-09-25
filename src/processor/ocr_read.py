
# Placeholder OCR (file-name based). For production, call Azure AI Vision Read API.
# If you want to wire real OCR, add the REST call here.
from .anpr_detect import detect_plate_from_name

def ocr_plate(blob_name: str, image_bytes: bytes):
    plate = detect_plate_from_name(blob_name)
    confidence = 0.92 if plate else 0.0
    return plate, confidence
