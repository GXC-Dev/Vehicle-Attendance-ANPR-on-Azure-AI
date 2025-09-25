
# Minimal placeholder plate detection:
# In production, use a detector (YOLO) and crop + OCR.
# Here we attempt to get plate from filename like IMG_<PLATE>_*.png
import re, os

PLATE_RE = re.compile(r'([A-Z0-9]{2,3}-?[A-Z0-9]{3})')

def detect_plate_from_name(blob_name: str):
    base = os.path.basename(blob_name).upper()
    m = PLATE_RE.search(base.replace('_','-'))
    if m:
        return m.group(1).replace('-', '')
    return None
