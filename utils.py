import os
import time
import cv2
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

def run_model_yolo(model_i, model_t, filepath):
    """
    Ensemble logic: 
    model_i = I-Beam Expert (Exp 4 @ 960px)
    model_t = T-Beam Expert (Exp 10 @ 1024px)
    """
    filename = os.path.basename(filepath)
    base_name = filename.split('.')[0]
    is_video = filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
    processed_dir = os.path.join("static", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    batch_id = int(time.time())
    
    # 1. RUN I-BEAM EXPERT (Class 0)
    # Stride 15 for videos to save CPU, imgsz matches training
    results_i_gen = model_i.predict(source=filepath, classes=[0], conf=0.4, imgsz=960, vid_stride=15 if is_video else 1, stream=True)
    results_i = list(results_i_gen)

    # 2. RUN T-BEAM EXPERT (Class 1)
    results_t_gen = model_t.predict(source=filepath, classes=[1], conf=0.15, imgsz=1024, vid_stride=15 if is_video else 1, stream=True)
    results_t = list(results_t_gen)

    processed_filenames = []
    max_total = -1
    final_counts = {"ibeam": 0, "tbeam": 0, "total": 0}

    # Iterate through results (matching frames)
    for i in range(len(results_i)):
        res_i = results_i[i]
        res_t = results_t[i]

        # Extract specific counts
        c_i = extract_counts(res_i) # Should only find I-beams
        c_t = extract_counts(res_t) # Should only find T-beams
        
        current_total = c_i["ibeam"] + c_t["tbeam"]

        # 3. MERGE VISUALS
        # Plot I-beams first
        annotated_frame = res_i.plot()
        # Overlay T-beams on top of the same frame
        annotated_frame = res_t.plot(img=annotated_frame)

        # Save the merged frame
        frame_name = f"proc_{i}_{batch_id}_{base_name}.jpg"
        save_path = os.path.join(processed_dir, frame_name)
        cv2.imwrite(save_path, annotated_frame) 
        processed_filenames.append(frame_name)

        # Keep track of the frame with the best detection count for the final report
        if current_total > max_total:
            final_counts = {
                "ibeam": c_i["ibeam"],
                "tbeam": c_t["tbeam"],
                "total": current_total
            }
            max_total = current_total

    return {"processed_files": processed_filenames, "counts": final_counts, "is_video": is_video}

def extract_counts(result):
    c_dict = {"ibeam": 0, "tbeam": 0, "total": 0}
    if result.boxes is not None:
        for c in result.boxes.cls:
            # Get class name from model names dictionary
            label = result.names[int(c)].lower().replace(" ", "").replace("-", "")
            if "ibeam" in label: 
                c_dict["ibeam"] += 1
            elif "tbeam" in label: 
                c_dict["tbeam"] += 1
    c_dict["total"] = c_dict["ibeam"] + c_dict["tbeam"]
    return c_dict