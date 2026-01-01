import torch
from ultralytics import YOLO
from flask import Flask, render_template, request, redirect
from utils import save_uploaded_files, run_model_yolo
from db import init_db

app = Flask(__name__)

# Load YOLO ONCE
MODEL_PATH = "models/yolo_beam.pt"
model = YOLO(MODEL_PATH)
model.to("cpu")  # REQUIRED for Render


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/process_upload", methods=["POST"])
def process_upload():
    files = request.files.getlist("media")
    if not files or files[0].filename == "":
        return redirect("/upload")

    saved = save_uploaded_files(files)
    _, path = saved[0]

    result = run_model_yolo(model, path)

    return render_template(
        "verify.html",
        processed_file=result["processed_file"],
        counts=result["counts"]
    )


@app.route("/verify")
def verify():
    return render_template(
        "verify.html",
        processed_file=None,
        counts={"I-beam": 0, "T-beam": 0, "Total": 0}
    )


@app.route("/history")
def history():
    return render_template("history.html", entries=[])


@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/logout")
def logout():
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
