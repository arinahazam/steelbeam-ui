import os
import time
from ultralytics import YOLO

def save_uploaded_files(files):
    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    saved_info = []
    for file in files:
        # Use a single timestamp for the batch ID
        filename = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
        path = os.path.join(upload_dir, filename)
        file.save(path)
        saved_info.append((filename, path))
    return saved_info

def run_model_yolo(model, filepath):
    filename = os.path.basename(filepath)
    base_name = filename.split('.')[0]
    is_video = filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
    processed_dir = os.path.join("static", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    # Generate ONE batch_id for all frames in this file
    batch_id = int(time.time())
    
    # Predict frames - stride helps prevent over-processing videos
    results_gen = model.predict(source=filepath, conf=0.15, imgsz=960, vid_stride=15 if is_video else 1, stream=True)
    results = list(results_gen)

    processed_filenames = []
    for i, res in enumerate(results):
        # Unique filename pattern
        frame_name = f"proc_{i}_{batch_id}_{base_name}.jpg"
        save_path = os.path.join(processed_dir, frame_name)
        res.save(filename=save_path) 
        processed_filenames.append(frame_name)

    # Summary: Frame with the highest count
    max_total = -1
    counts = {"ibeam": 0, "tbeam": 0, "total": 0}
    for res in results:
        c = extract_counts(res)
        if c["total"] > max_total:
            counts = c
            max_total = c["total"]

    return {"processed_files": processed_filenames, "counts": counts, "is_video": is_video}

def extract_counts(result):
    c_dict = {"ibeam": 0, "tbeam": 0, "total": 0}
    if result.boxes is not None:
        for c in result.boxes.cls:
            label = result.names[int(c)].lower().replace(" ", "").replace("-", "")
            if "ibeam" in label: c_dict["ibeam"] += 1
            elif "tbeam" in label: c_dict["tbeam"] += 1
    c_dict["total"] = c_dict["ibeam"] + c_dict["tbeam"]
    return c_dict