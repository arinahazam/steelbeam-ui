from flask import Flask, render_template, request, redirect, url_for
from utils import save_uploaded_files
from hf_client import run_model_hf
from db import init_db, save_history
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/process_upload", methods=["POST"])
def process_upload():
    files = request.files.getlist("media")
    if not files or files[0].filename == "":
        return redirect("/upload")

    filename, filepath = save_uploaded_files(files)[0]

    result = run_model_hf(filepath)

    save_history(
        filename=filename,
        ibeam=result["summary"]["I-beam"],
        tbeam=result["summary"]["T-beam"],
        total=result["summary"]["Total"]
    )

    return render_template(
        "verify.html",
        processed_file=result["processed_file"],
        counts=result["summary"]
    )

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/history")
def history():
    from db import fetch_history
    return render_template("history.html", entries=fetch_history())

@app.route("/logout")
def logout():
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
