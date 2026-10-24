# 🚗 Vehicle Forensics Web

**A browser-based vehicle simulation and digital forensics analysis prototype.**

Vehicle Forensics Web is an educational project that combines a driving simulator with a local forensic dashboard to demonstrate how simulated vehicle telemetry can be collected, analyzed, and presented as digital evidence.

The project consists of two independent components:

* **Driving Simulator:** Simulates driving sessions, collisions, loss of control, and remote-hijack scenarios.
* **Forensics Dashboard:** Analyzes uploaded telemetry CSV files, identifies potential collision and remote-intervention indicators, visualizes findings, and generates PDF reports.

> **Disclaimer:** This project uses synthetic telemetry and rule-based analysis. Its findings are indicators for investigation, not proof of a real collision, vehicle compromise, or cyberattack.

---

## 📌 Table of Contents

* [Project Overview](#-project-overview)
* [Key Features](#-key-features)
* [Technology Stack](#-technology-stack)
* [Requirements](#-requirements)
* [Installation and Setup](#-installation-and-setup)
* [Running the Simulator](#-running-the-simulator)
* [Analyzing Evidence](#-analyzing-evidence)
* [CSV Format](#-csv-format)
* [Analysis Methodology](#-analysis-methodology)
* [Project Structure](#-project-structure)
* [Limitations](#-limitations)
* [Future Improvements](#-future-improvements)

---

## 🔍 Project Overview

Vehicle Forensics Web demonstrates a basic digital-forensics workflow using simulated vehicle telemetry.

The system allows users to generate driving-session evidence, transfer telemetry to a local analysis dashboard, examine potential incident indicators, and export a PDF report.

### How It Works

1. **Simulate:** Run a driving session and generate synthetic telemetry.
2. **Export:** Download the session evidence from the simulator.
3. **Import:** Extract the evidence ZIP and upload `telemetry.csv` to the dashboard.
4. **Analyze:** Validate the CSV, calculate its SHA-256 hash, and apply rule-based checks.
5. **Visualize:** Review telemetry charts, potential incident indicators, and the event timeline.
6. **Report:** Generate a PDF containing the analysis results and evidence metadata.

**Important:** The simulator and dashboard operate independently. Evidence must be transferred manually; there is no live telemetry connection between them.

---

## ✨ Key Features

### 🚘 Driving Simulator

* Browser-based driving simulation.
* Multiple driving and incident scenarios.
* Keyboard and touch controls.
* Adjustable camera and driving settings.
* Simulated collision and loss-of-control events.
* Simulated remote-hijack scenarios.
* Telemetry and event logging.
* Downloadable evidence files and case ZIP bundles.

### 🔬 Forensics Dashboard

* CSV upload and input validation.
* Sample accident and hijacking datasets.
* SHA-256 evidence hashing.
* Rule-based collision-indicator detection.
* Possible remote-intervention indicator detection.
* Interactive telemetry charts.
* Forensic event timeline.
* Evidence metadata and analysis summaries.
* PDF report generation.

### 📁 Evidence Management

The application uses local folders to organize its files:

* `data/` — sample telemetry datasets.
* `uploads/` — uploaded evidence files.
* `reports/` — generated PDF reports.

---

## 🛠️ Technology Stack

| Technology             | Purpose                                     |
| ---------------------- | ------------------------------------------- |
| Python                 | Backend logic and telemetry analysis        |
| Flask                  | Local web application                       |
| HTML5                  | Web interfaces and simulator structure      |
| CSS3                   | Interface styling                           |
| JavaScript             | Driving simulation and browser interactions |
| CSV                    | Telemetry data exchange                     |
| SHA-256                | Evidence file integrity checking            |
| Chart.js               | Telemetry visualization                     |
| PDF generation library | Exporting forensic analysis reports         |

---

## 💻 Requirements

Before running the project, ensure you have:

* Python 3.10 or newer.
* Google Chrome, Microsoft Edge, or another modern browser.
* pip for installing Python dependencies.
* Internet access for loading Chart.js from its CDN.

The simulator runs directly in a browser and does not require the Flask server.

---

## ⚙️ Installation and Setup

### Step 1: Open the Project

Open the `VehicleForensicsWeb` folder in VS Code or a terminal.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Start the Dashboard

```bash
python app.py
```

Open the following address in your browser:

**http://127.0.0.1:5000**

Keep the terminal open while using the application. Press `Ctrl+C` in the terminal to stop the server.

### Step 5: Load a Demonstration Dataset

Use the dashboard's **Demo Accident** or **Demo Hijacking** option to load the corresponding sample dataset.

You can also upload your own compatible telemetry CSV file.

---

## 🎮 Running the Simulator

Open `vehicle_forensics_game_v2.html` directly in Chrome or Edge.

### Getting Started

1. Select a scenario from the simulator menu.
2. Click **START** to begin the driving session.
3. Drive using the available controls or use a scenario that triggers an event automatically.
4. Select **REMOTE HIJACK** to demonstrate a simulated remote-control event during a running session.
5. Use **END HIJACK** to stop a manually initiated hijack.
6. Click **EXPORT CASE** to export the session evidence.
7. Choose **DOWNLOAD FULL CASE (.zip)** or download an individual evidence file.

### Available Scenarios

Examples include:

* Normal Driving.
* Rear-End Collision.
* Remote Hijack.
* Remote Hijack → Accident.

Actual scenario names depend on the options implemented in the simulator.

### Simulator Controls

| Key       | Action                                |
| --------- | ------------------------------------- |
| `W` / `↑` | Accelerate                            |
| `S` / `↓` | Brake or reverse                      |
| `A` / `←` | Steer left                            |
| `D` / `→` | Steer right                           |
| `Space`   | Handbrake                             |
| `H`       | Start the selected remote-hijack mode |
| `P`       | Pause or resume                       |
| `R`       | Reset the car                         |
| `C`       | Change camera                         |

Touch controls are also available on supported devices.

---

## 📊 Analyzing Evidence

To analyze evidence generated by the simulator:

1. Start the Flask dashboard.
2. Open the simulator and complete a driving session.
3. Click **EXPORT CASE**.
4. Download the full case ZIP.
5. Extract the ZIP and locate `telemetry.csv`.
6. Return to the dashboard and select the CSV.
7. Click **Analyze Evidence**.
8. Review the evidence hash, record count, chart, incident indicators, and event timeline.
9. Select **Generate PDF** to create a report for the analyzed case.

### Exported Evidence Files

The simulator may export supporting files such as:

* `telemetry.csv`
* `can_frames.csv`
* `events.csv`
* `timeline.csv`
* `remote_intervention_log.json`
* `summary.json`
* `evidence_manifest.json`

These files contain simulated information from the driving session.

The dashboard's CSV uploader analyzes `telemetry.csv`; it does not automatically import or analyze the complete ZIP bundle.

### Timestamp Handling

The simulator exports ISO-formatted timestamps, while the dashboard currently expects numeric timestamps.

For simulator-generated files, the dashboard substitutes row order when handling these timestamps. Consequently, the displayed times represent sample order rather than actual elapsed seconds.

The included demonstration CSV files use numeric timestamps.

---

## 📄 CSV Format

The dashboard requires the following columns:

```csv
timestamp,speed_kmh,acceleration_mps2,brake,steering_deg,x,y
```

Optional columns:

```csv
remote_command,event
```

### Column Descriptions

| Column              | Description                                                      |
| ------------------- | ---------------------------------------------------------------- |
| `timestamp`         | Numeric timestamp, such as seconds from the start of a recording |
| `speed_kmh`         | Vehicle speed in kilometres per hour                             |
| `acceleration_mps2` | Acceleration in metres per second squared                        |
| `brake`             | Boolean-like or numeric braking value                            |
| `steering_deg`      | Steering angle in degrees                                        |
| `x`                 | X-coordinate of the simulated vehicle                            |
| `y`                 | Y-coordinate of the simulated vehicle                            |
| `remote_command`    | Optional remote-command indicator                                |
| `event`             | Optional event label, such as `COLLISION` or `REMOTE_COMMAND`    |

Additional CSV handling details:

* Column headers are case-insensitive.
* Common aliases such as `time`, `speed`, `accel`, `steering`, `pos_x`, `pos_y`, `remote`, and `events` are accepted.
* Comma, semicolon, tab, and pipe delimiters are supported.
* Rows are sorted by timestamp.
* Maximum upload size: **25 MB**.

---

## 🧪 Analysis Methodology

The dashboard uses transparent, rule-based heuristics to identify telemetry patterns that may warrant further investigation.

### 1. Evidence Integrity

The application calculates a SHA-256 hash for the uploaded file.

When generating a PDF report, the dashboard checks the file hash again to help identify changes to the stored evidence file after import.

A matching hash supports file-integrity verification, but it does not independently establish the authenticity or origin of the evidence.

### 2. Collision Indicators

The dashboard checks for patterns such as:

* Severe deceleration.
* Sharp decreases in vehicle speed.
* Braking-related patterns.
* Explicit collision event markers.

These patterns may indicate a possible collision but can also occur during other driving situations.

### 3. Possible Remote Intervention

The dashboard checks for patterns such as:

* Explicit remote-command markers.
* Remote-related event labels.
* Unusual acceleration combined with abrupt steering changes.

These patterns may warrant review but do not independently establish that a vehicle was remotely controlled or compromised.

### 4. Visualization and Reporting

The dashboard presents its findings through telemetry charts, event tables, and a forensic timeline.

A PDF report summarizes the available evidence, hash information, analysis results, and interpretation limitations.

---

## 📂 Project Structure

```text
VehicleForensicsWeb/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── vehicle_forensics_game_v2.html
├── data/
│   ├── accident_demo.csv
│   └── hijacking_demo.csv
├── uploads/
└── reports/
```

| File or Folder                   | Purpose                                                             |
| -------------------------------- | ------------------------------------------------------------------- |
| `app.py`                         | Flask application, telemetry analysis, and report-generation routes |
| `requirements.txt`               | Python dependency list                                              |
| `templates/index.html`           | Dashboard interface                                                 |
| `vehicle_forensics_game_v2.html` | Standalone driving simulator                                        |
| `data/`                          | Sample telemetry datasets                                           |
| `uploads/`                       | Locally stored uploaded evidence                                    |
| `reports/`                       | Generated PDF reports                                               |

The application creates `uploads/`, `reports/`, and `data/` if they do not already exist.

Uploaded evidence and generated reports are stored locally.

---

## ⚠️ Limitations

This project is an educational prototype and has the following limitations:

* All simulator telemetry is synthetic.
* No physical vehicle or real CAN bus is connected.
* The dashboard does not collect live vehicle telemetry.
* Evidence transfer between the simulator and dashboard is manual.
* The dashboard relies on heuristic rules rather than a validated accident-reconstruction method.
* Timestamp handling for simulator-generated CSV files currently falls back to row order.
* SHA-256 hashing does not independently establish evidence authenticity.
* Flagged events are not definitive proof of a collision, remote intervention, or cyberattack.
* The project is not a substitute for professional digital-forensics tools or independent investigation.

Real-world conclusions would require corroboration from appropriate vehicle records, ECU/CAN data, network logs, device evidence, reliable timestamps, and physical evidence.

---

## 🚀 Future Improvements

Potential improvements include:

* Support for ISO-formatted timestamps and elapsed-time calculations.
* Automatic extraction and processing of simulator evidence ZIP files.
* More detailed telemetry analysis and configurable detection thresholds.
* Improved evidence provenance and audit logging.
* Additional visualizations and incident comparison tools.
* Expanded export formats and investigation summaries.
* Integration with recorded vehicle telemetry for controlled research environments.

These are potential extensions and should not be considered implemented features unless added to the project.

---

## 🎓 Intended Use

Vehicle Forensics Web is intended for educational demonstrations, software development practice, and exploration of vehicle telemetry analysis and digital-forensics workflows.

It should not be used as the sole basis for real-world accident investigations, cybersecurity incident attribution, or legal conclusions.
