from gradio_client import Client
import os
import shutil
import uuid

client = Client("arinahzm/steelbeam")

PROCESSED_DIR = "static/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def run_model_hf(image_path):
    # IMPORTANT: pass FILE PATH as dict
    result_img, summary = client.predict(
        img={"path": os.path.abspath(image_path)},
        api_name="/infer"
    )

    output_name = f"{uuid.uuid4().hex}.png"
    output_path = os.path.join(PROCESSED_DIR, output_name)

    shutil.copy(result_img["path"], output_path)

    return {
        "processed_file": output_name,
        "summary": summary
    }