INDUSTRIAL STEEL BEAM COUNTING & SEGMENTATION SYSTEM Official Project Documentation | Innonics Sdn. Bhd. Date: January 2026

Version: 1.0 (Ensemble Production)

1. PROJECT OVERVIEW This system provides an automated solution for inventory tracking of I-Beams and T-Beams.

2. The system does not rely on a single model. Instead, it runs two "Expert" models in parallel:

I-Beam Expert (Model 4): A YOLOv8 Nano architecture trained at 960px. This model provides high precision for standard heavy structural beams.

T-Beam Expert (Model 10): A YOLOv8 Small architecture trained at 1024px. This higher resolution and larger model capacity allow the system to detect the fine "stem" of T-beams that are often missed by smaller models.

The system merges the results of both models in real-time to provide a single, unified count and visual display.

3. TECHNICAL SPECIFICATIONS * Backend: Flask (Python)

AI Engine: Ultralytics YOLOv8 (Instance Segmentation)

Database: SQLite3

Reporting: CSV (Production Metrics) and FPDF (Official Documentation)

Input Formats: JPG, PNG, WEBP, MP4, AVI, MOV

4. SETUP & INSTALLATION 
Step 1: Clone the Repository Open your terminal or command prompt and run:

git clone https://github.com/arinahazam/steelbeam-ui.git
cd steelbeam-ui

Step 2: Environment Configuration Create and activate a virtual environment to isolate dependencies:

python -m venv venv

.\venv\Scripts\activate (Windows)

source venv/bin/activate (Mac/Linux)

Step 3: Dependency Installation Install all required libraries including PyTorch, YOLO, and Flask:

pip install -r requirements.txt

Step 4: Ensure the following files are present in the /models directory:

model4_i_expert.pt

model10_t_expert.pt

5. OPERATIONAL WORKFLOW 

5.1. Launch: Run python app.py and navigate to http://127.0.0.1:5000. and Log in/Sign up to access 

5.2. Upload: Use the Dashboard to upload batch photos or videos from the warehouse.

5.3. Verify: Review the AI-generated segmentation masks. The system will display different colored masks for I-beams and T-beams. User choose to reject/approve

5.4. Approve: Once verified, the data is committed to the permanent history.

5.5. Report: Generate a PDF Production Summary for the shift supervisor.

5.6. MAINTENANCE & CONTACT This repository is managed under Git version control. For updates to the detection thresholds, modify the confidence (conf) parameters in the run_model_yolo function within utils.py.
