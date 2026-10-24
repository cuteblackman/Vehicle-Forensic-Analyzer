# Vehicle Forensics Web

A local vehicle-forensics prototype with two parts:

- **Forensics dashboard** — a Flask web app for uploading telemetry CSV files, reviewing accident and possible remote-intervention indicators, and generating a PDF report.
- **Driving simulator** — a standalone browser game that creates simulated driving, collision, and remote-hijack scenarios and exports a case evidence bundle.

The dashboard and simulator are separate tools. The simulator does not send live data to the dashboard; transfer its exported telemetry CSV manually.

> **Important:** Simulator output is synthetic. The dashboard's findings are rule-based indicators, not proof of a real collision, vehicle compromise, or cyberattack.

## Project explanation

This project is an educational prototype for exploring how vehicle telemetry can be collected, organized, and reviewed during a basic forensic investigation. It combines a browser-based driving simulation with a local analysis dashboard:

1. The simulator creates a driving session and can record normal driving, collisions, loss of control, and simulated remote-control activity.
2. The simulator packages that session as downloadable evidence files. The evidence is generated from the game's internal state; it is not captured from a physical vehicle or a real CAN bus.
3. The dashboard accepts a telemetry CSV, calculates an evidence hash, checks the data for patterns associated with collisions or possible remote intervention, and presents the results in charts and tables.
4. The user can create a PDF summary to retain the file hash, analysis results, event timeline, and interpretation limitations.

The two parts are intentionally loosely connected: the simulator exports files in the browser, and the user manually uploads `telemetry.csv` to the dashboard. The Flask app does not control the simulator, collect live telemetry, connect to a vehicle, or automatically import the ZIP bundle.

### Main parts

- **Simulator (`vehicle_forensics_game_v2.html`):** a self-contained driving game with selectable scenarios, keyboard/touch controls, camera and driving settings, and simulated incident controls. During a run it records telemetry and supporting event, timeline, CAN-like, and remote-intervention data. **CAN-like** means formatted to resemble example signal records; it is not real vehicle bus traffic.
- **Dashboard (`app.py` and `templates/index.html`):** a local Flask application with sample datasets, CSV upload and validation, heuristic analysis, evidence metadata, an interactive chart, a forensic timeline, and PDF generation.
- **Evidence folders (`data/`, `uploads/`, and `reports/`):** demo CSV inputs, locally saved user uploads, and generated PDF reports, respectively.

### What the analysis is intended to show

The dashboard demonstrates a simple evidence-review workflow rather than a certified forensic method. It checks whether the file changes after import using SHA-256, then applies transparent rules to identify candidate events. For example, a sharp speed drop, strong deceleration, or a collision event label may contribute to a collision indication. A remote-command marker, remote-related event label, or a combination of unusual acceleration and abrupt steering may contribute to a possible remote-intervention indication. Results are shown alongside their telemetry context so they can be reviewed rather than treated as automatic proof.

This makes the project useful for demonstrating telemetry intake, evidence integrity checks, event visualization, and report generation with reproducible simulated scenarios. It does not implement a vehicle connection, a validated accident reconstruction method, or a real cyberattack detector.

## Requirements

- Python 3.10 or newer
- A modern browser such as Chrome or Edge
- Internet access for the dashboard chart (Chart.js is loaded from a CDN). Other dashboard features work without the chart library.

## Start the dashboard

Open PowerShell or Command Prompt in the project folder and run:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. Keep the terminal window open while using the dashboard; press `Ctrl+C` there to stop the server.

The dashboard initially loads the included accident demo. Use **Demo Accident** or **Demo Hijacking** to load either sample again, or upload your own evidence using **Select telemetry CSV** and **Analyze Evidence**.

## Run the simulator

Open `vehicle_forensics_game_v2.html` in Chrome or Edge. It runs in the browser and does not need to be served by Flask.

1. Choose a scenario, such as **Normal Driving**, **Rear-End Collision**, **Remote Hijack**, or **Remote Hijack → Accident**.
2. Click **START** and drive, or use a scenario that triggers an event automatically.
3. Click **REMOTE HIJACK** during a running session to demonstrate a remote-control event. Select the hijack mode and duration first; use **END HIJACK** to stop a manual hijack.
4. Click **EXPORT CASE**, then choose **DOWNLOAD FULL CASE (.zip)** or download an individual evidence file.

### Simulator controls

| Control | Action |
| --- | --- |
| `W` / `↑` | Accelerate |
| `S` / `↓` | Brake or reverse |
| `A` / `←`, `D` / `→` | Steer |
| `Space` | Handbrake |
| `H` | Start the selected remote-hijack mode |
| `P` | Pause or resume |
| `R` | Reset the car |
| `C` | Change camera |

Touch controls are also available on supported touch devices. Scenario, traffic, camera, and steering options are available in the simulator's menus.

## Analyze simulator evidence in the dashboard

1. Export and download the simulator's full case ZIP.
2. Extract the ZIP and locate **`telemetry.csv`**.
3. In the dashboard, select that CSV and choose **Analyze Evidence**.
4. Review the evidence hash, record count, chart, collision indication, remote-intervention indicators, and event timeline.
5. Select **Generate PDF** to download a report for the most recently analyzed case.

The simulator also exports supporting files such as `can_frames.csv`, `events.csv`, `timeline.csv`, `remote_intervention_log.json`, `summary.json`, and `evidence_manifest.json`. These provide additional simulated context; the dashboard's CSV uploader analyzes `telemetry.csv`.

**Timestamp note:** The simulator writes ISO date/time values in the telemetry `timestamp` column. The dashboard currently expects numeric timestamps, so it substitutes row order for these values. Analysis still runs, but displayed times for simulator uploads represent sample order rather than elapsed seconds. The included demo CSV files use numeric times.

## CSV format for other evidence

The dashboard requires these columns:

```csv
timestamp,speed_kmh,acceleration_mps2,brake,steering_deg,x,y
```

Optional columns:

```csv
remote_command,event
```

- `timestamp` should be numeric (for example, seconds from the beginning of the recording).
- `speed_kmh` is speed in km/h; `acceleration_mps2` is acceleration in m/s².
- `brake` can be a boolean-like value (`1`/`0`, `true`/`false`, `yes`/`no`) or a numeric value.
- `steering_deg`, `x`, and `y` should be numeric.
- `remote_command` marks a remote command; `event` can contain event labels such as `COLLISION` or `REMOTE_COMMAND`.
- Headers are case-insensitive. Common aliases such as `time`, `speed`, `accel`, `steering`, `pos_x`, `pos_y`, `remote`, and `events` are accepted.
- Comma, semicolon, tab, and pipe delimiters are supported. Rows are sorted by timestamp.
- Maximum upload size: **25 MB**.

## What the dashboard checks

- **Evidence integrity:** calculates a SHA-256 hash for the imported file and checks it again when creating the PDF report.
- **Collision indication:** flags candidate events using severe deceleration, a sharp speed drop, braking, or an explicit collision event marker.
- **Possible remote intervention:** flags explicit remote-command/event markers or combinations of unusual acceleration and abrupt steering changes.
- **Timeline and report:** displays flagged events and creates a PDF with evidence metadata, analysis results, and limitations.

These checks are heuristic. A flagged event is not a definitive conclusion; validate findings against independent vehicle, ECU/CAN, network, device, timestamp, and physical evidence.

## Project layout

```text
VehicleForensicsWeb/
├── app.py                         # Flask app and CSV analysis/report routes
├── requirements.txt               # Python dependencies
├── templates/
│   └── index.html                 # Dashboard interface
├── vehicle_forensics_game_v2.html # Standalone simulator
├── data/
│   ├── accident_demo.csv
│   └── hijacking_demo.csv
├── uploads/                       # Uploaded evidence files
└── reports/                       # Generated PDF reports
```

The app creates `uploads/`, `reports/`, and `data/` if they do not already exist. Uploaded CSV files and generated reports are stored locally in those folders.
#   V e h i c l e - F o r e n s i c - A n a l y z e r  
 #   V e h i c l e - F o r e n s i c - A n a l y z e r  
 