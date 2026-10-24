# Vehicle Forensics Web Dashboard

A polished local web application for:
- telemetry evidence intake
- SHA-256 evidence integrity
- accident/collision indication
- remote-intervention indicators
- forensic timeline
- PDF report generation
- demo accident and hijacking datasets

## Run on Windows

1. Install Python 3.10+.
2. Open Command Prompt in this folder.
3. Run:
   python -m pip install -r requirements.txt
4. Run:
   python app.py
5. Open:
   http://127.0.0.1:5000

The dashboard loads a demo accident case automatically.

Use "Demo Hijacking" to load the controlled remote-intervention dataset.

## Your own evidence

Upload a CSV with:
timestamp,speed_kmh,acceleration_mps2,brake,steering_deg,x,y

Optional:
remote_command,event

## BeamNG

The web application is simulator-independent. Once BeamNG telemetry is available, export/collect it into the same CSV schema and upload it. A BeamNG-specific bridge should be matched to the exact BeamNG.drive/BeamNG.tech version because API availability differs between editions and versions.

## Important forensic limitation

The application generates investigative indicators from telemetry. It does not prove that a real vehicle was hacked. Correlate with independent CAN/ECU/network/device/physical evidence.
