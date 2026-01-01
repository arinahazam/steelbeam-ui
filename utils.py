import os
import time
import cv2
from ultralytics import YOLO

UPLOAD_DIR = "static/uploads"
PROCESSED_DIR = "static/processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def save_uploaded_files(files):
    saved = []
    for f in files:
        filename = f"{int(time.time())}_{f.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        f.save(path)
        saved.append((filename, path))
    return saved


def run_model_yolo(model, image_path):
    results = model(image_path)[0]

    # Count classes
    counts = {"I-beam": 0, "T-beam": 0, "Total": 0}

    if results.boxes is not None:
        cls_ids = results.boxes.cls.tolist()
        names = results.names

        for cid in cls_ids:
            label = names[int(cid)]
            if label in counts:
                counts[label] += 1
                counts["Total"] += 1

    # Save visualized output
    output_filename = f"processed_{int(time.time())}.png"
    output_path = os.path.join(PROCESSED_DIR, output_filename)

    annotated = results.plot()
    cv2.imwrite(output_path, annotated)

    return {
        "processed_file": output_filename,
        "counts": counts
    }
