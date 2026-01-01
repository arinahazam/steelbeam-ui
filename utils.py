import os
import time

UPLOAD_DIR = "static/uploads"

def save_uploaded_files(files):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved = []

    for f in files:
        filename = f"{int(time.time())}_{f.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        f.save(path)
        saved.append((filename, path))

    return saved
