import os
import sqlite3
import csv
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify, flash, make_response
from ultralytics import YOLO
from fpdf import FPDF

# Import your local helper scripts
from db import init_db
from utils import save_uploaded_files, run_model_yolo

app = Flask(__name__)
app.secret_key = "industrial_steel_secret" 

# --- DYNAMIC PATH CONFIGURATION ---
# This ensures the app works on ANY computer (Windows/Mac/GitHub)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "steelbeam.db")
MODEL_PATH = os.path.join(BASE_DIR, "models", "yolo_beam.pt")

# --- MEDIA VALIDATION ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load Model
model = YOLO(MODEL_PATH)
model.to("cpu")

@app.route("/")
def index(): 
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        session["user_id"] = request.form.get("username")
        return redirect(url_for("dashboard"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user_id"] = request.form.get("username")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for('index'))
    return render_template("dashboard.html")

@app.route("/upload", methods=["GET", "POST"])
def upload_page(): 
    if "user_id" not in session: return redirect(url_for('index'))
    return render_template("upload.html")

@app.route("/process_upload", methods=["POST"])
def process_upload():
    if "user_id" not in session: return redirect(url_for('index'))
    
    files = request.files.getlist("media")
    if not files or files[0].filename == "": 
        flash("Please select a file to upload.")
        return redirect(url_for("upload_page"))

    # Validate file formats
    for file in files:
        if not allowed_file(file.filename):
            flash(f"Media format not supported: {file.filename}. Use JPG, PNG, or MP4.")
            return redirect(url_for("upload_page"))

    session_results = []
    conn = None
    
    try:
        # timeout=10 prevents the "Database is locked" error
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cur = conn.cursor()

        for file in files:
            saved = save_uploaded_files([file])
            fname, fpath = saved[0]
            res = run_model_yolo(model, fpath)
            
            primary_file = res["processed_files"][0]
            cur.execute("""
                INSERT INTO history (filename, processed_file, ibeam, tbeam, total, status, employee_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (fname, primary_file, res["counts"]["ibeam"], res["counts"]["tbeam"], 
                  res["counts"]["total"], "PENDING", session.get("user_id", "Unknown"), 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            session_results.append({
                "history_id": cur.lastrowid,
                "filename": fname,
                "processed_files": res["processed_files"],
                "counts": res["counts"],
                "is_video": res["is_video"]
            })

        conn.commit()
    except sqlite3.OperationalError as e:
        flash("Database error occurred. Please try again.")
        return redirect(url_for("upload_page"))
    finally:
        if conn:
            conn.close()

    return render_template("verify.html", results=session_results)

@app.route("/verify")
def verify_page(): 
    if "user_id" not in session: return redirect(url_for('index'))
    return render_template("verify.html")

@app.route("/verify_decision", methods=["POST"])
def verify_decision():
    h_id = request.form.get("history_id")
    status_received = request.form.get("status") 
    final_status = "APPROVED" if status_received == "APPROVED" else "REJECTED"
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cur = conn.cursor()
        cur.execute("UPDATE history SET status = ? WHERE id = ?", (final_status, h_id))
        conn.commit()
    finally:
        if conn: conn.close()
    return jsonify({"status": "success"})

@app.route("/history")
def history():
    if "user_id" not in session: return redirect(url_for('index'))
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM history WHERE status != 'PENDING' ORDER BY created_at DESC")
    entries = cur.fetchall()
    conn.close()
    return render_template("history.html", entries=entries)

@app.route("/report")
def report():
    if "user_id" not in session: return redirect(url_for('index'))
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM history WHERE status != 'PENDING' ORDER BY created_at DESC")
    entries = cur.fetchall()
    
    stats = {
        "total_beams": sum(row['total'] for row in entries),
        "approved": sum(1 for row in entries if row['status'] == 'APPROVED'),
        "rejected": sum(1 for row in entries if row['status'] == 'REJECTED')
    }
    conn.close()
    return render_template("report.html", entries=entries, stats=stats)

@app.route('/export_report')
def export_report():
    ids_raw = request.args.get('ids', '')
    if not ids_raw: return "No records selected", 400
    id_list = ids_raw.split(',')

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Expert Tip: Removed Filename from the query to keep data focused on production metrics
    query = f"SELECT created_at, employee_id, ibeam, tbeam, total, status FROM history WHERE id IN ({','.join(['?']*len(id_list))})"
    cur.execute(query, id_list)
    rows = cur.fetchall()
    conn.close()

    si = io.StringIO()
    cw = csv.writer(si)

    # 1. Company Branding & Metadata (Expert standard for CSV headers)
    cw.writerow(['COMPANY:', 'Innonics Sdn. Bhd.'])
    cw.writerow(['REPORT:', 'Industrial Production Summary'])
    cw.writerow(['GENERATED:', datetime.now().strftime('%Y-%m-%d %H:%M')])
    cw.writerow([])  # Empty line for readability

    # 2. Main Data Headers
    cw.writerow(['Date', 'Verifier (ID)', 'I-Beam', 'T-Beam', 'Batch Total', 'Status'])

    # 3. Data Rows & Calculations
    grand_i = 0
    grand_t = 0
    grand_total = 0

    for row in rows:
        cw.writerow(row)
        grand_i += row[2]     # Index 2 is ibeam
        grand_t += row[3]     # Index 3 is tbeam
        grand_total += row[4] # Index 4 is total

    # 4. Summary Totals Row (Crucial for inventory managers)
    cw.writerow([]) # Spacer
    cw.writerow(['GRAND TOTALS', '', grand_i, grand_t, grand_total, 'VERIFIED'])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Innonics_Production_Report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/export_pdf')
def export_pdf():
    ids_raw = request.args.get('ids', '')
    if not ids_raw: return "No records selected", 400
    id_list = ids_raw.split(',')

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    placeholders = ','.join(['?'] * len(id_list))
    query = f"SELECT employee_id, status, created_at, ibeam, tbeam, total FROM history WHERE id IN ({placeholders})"
    cur.execute(query, id_list)
    rows = cur.fetchall()
    conn.close()

    # --- Initialize PDF ---
    pdf = FPDF()
    pdf.add_page()
    
   # 1. PRIMARY HEADER: Company Identity
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 45, 98)
    pdf.cell(0, 8, "INNONICS SDN. BHD.", ln=True, align="L") # Official Company Name
    
    pdf.set_font("helvetica", "B", 20)
    pdf.cell(0, 12, "INDUSTRIAL PRODUCTION SUMMARY", ln=True, align="L")
    
    # 2. Metadata Information
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)

    # --- Table Header ---
    pdf.set_fill_color(0, 45, 98) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 10)
    
    # Cleaned Headers (Removed Filename)
    headers = ["Date", "Employee", "I-Beam", "T-Beam", "Batch Total", "Status"]
    widths = [35, 35, 30, 30, 30, 30]
    
    for i in range(len(headers)):
        pdf.cell(widths[i], 10, headers[i], border=1, align="C", fill=True)
    pdf.ln()

    # --- Table Data & Calculation ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "", 10)
    
    grand_i = 0
    grand_t = 0
    grand_total = 0

    for row in rows:
        # Accumulate Totals
        grand_i += row['ibeam']
        grand_t += row['tbeam']
        grand_total += row['total']

        pdf.cell(widths[0], 10, str(row['created_at'])[:10], border=1, align="C")
        pdf.cell(widths[1], 10, str(row['employee_id']), border=1, align="C")
        pdf.cell(widths[2], 10, str(row['ibeam']), border=1, align="C")
        pdf.cell(widths[3], 10, str(row['tbeam']), border=1, align="C")
        pdf.cell(widths[4], 10, str(row['total']), border=1, align="C")
        pdf.cell(widths[5], 10, str(row['status']), border=1, align="C")
        pdf.ln()

    # --- Grand Totals Section (Industry Requirement) ---
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_fill_color(240, 240, 240) # Light grey highlight
    
    # We span the first two columns (35+35=70) as a label
    pdf.cell(70, 12, "PRODUCTION TOTALS", border=1, fill=True, align="R")
    pdf.cell(30, 12, str(grand_i), border=1, align="C", fill=True)
    pdf.cell(30, 12, str(grand_t), border=1, align="C", fill=True)
    pdf.set_text_color(0, 45, 98)
    pdf.cell(30, 12, str(grand_total), border=1, align="C", fill=True)
    pdf.cell(30, 12, "", border=1, fill=True) # Empty space under status
    pdf.ln(20)

    # 3. Validation Footer
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
   

    # --- Output ---
    pdf_bytes = bytes(pdf.output()) 
    response = make_response(pdf_bytes)
    response.headers["Content-Disposition"] = "attachment; filename=Production_Report.pdf"
    response.headers["Content-type"] = "application/pdf"
    return response

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)