
from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import csv, hashlib, io, json, math
from datetime import datetime
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

app = Flask(__name__)
DATA = Path(__file__).parent / "data"
REPORTS = Path(__file__).parent / "reports"
UPLOADS = Path(__file__).parent / "uploads"
REPORTS.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)
UPLOADS.mkdir(exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB upload limit

REQUIRED = ["timestamp","speed_kmh","acceleration_mps2","brake","steering_deg","x","y"]

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def f(v, default=0.0):
    try:
        x = float(v)
        return x if math.isfinite(x) else default
    except (TypeError, ValueError):
        return default

ALIASES = {
    "time":"timestamp","t":"timestamp","time_s":"timestamp",
    "speed":"speed_kmh","speed_kph":"speed_kmh","velocity":"speed_kmh",
    "accel":"acceleration_mps2","acceleration":"acceleration_mps2","acc":"acceleration_mps2","acceleration_ms2":"acceleration_mps2",
    "brake_pressed":"brake","braking":"brake","brake_input":"brake",
    "steering":"steering_deg","steer":"steering_deg","steering_angle":"steering_deg",
    "pos_x":"x","pos_y":"y",
    "remote":"remote_command","remote_cmd":"remote_command","remote_flag":"remote_command","hijack":"remote_command",
    "events":"event","label":"event",
}

def norm_header(h):
    h=(h or "").replace("\ufeff","").strip().lower().replace(" ","_")
    return ALIASES.get(h,h)

def b(v):
    v=str(v if v is not None else "").strip().lower()
    if v in {"1","true","yes","y","on","t"}: return True
    try: return float(v)>0
    except: return False

def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fp:
        text=fp.read()
    if not text.strip(): raise ValueError("The CSV has no records.")
    header=text.lstrip().splitlines()[0]
    delim=max(",;\t|",key=header.count)
    reader=csv.DictReader(io.StringIO(text,newline=""),delimiter=delim)
    raw=[]
    for r in reader:
        raw.append({norm_header(k):(v.strip() if isinstance(v,str) else v) for k,v in r.items() if k is not None})
    raw=[r for r in raw if any(str(v).strip() for v in r.values() if v is not None)]
    if not raw: raise ValueError("The CSV has no records.")
    missing=[c for c in REQUIRED if c not in raw[0]]
    if missing: raise ValueError("Missing columns: "+", ".join(missing))
    rows=[]
    for i,r in enumerate(raw):
        rows.append({
            "row":i,"timestamp":f(r.get("timestamp"),i),
            "speed_kmh":f(r.get("speed_kmh")),
            "acceleration_mps2":f(r.get("acceleration_mps2")),
            "brake":b(r.get("brake")),
            "steering_deg":f(r.get("steering_deg")),
            "x":f(r.get("x")),"y":f(r.get("y")),
            "remote_command":b(r.get("remote_command")),
            "event":str(r.get("event") or "").strip()
        })
    rows.sort(key=lambda r:r["timestamp"])   # chronological order (stable for ties)
    for i,r in enumerate(rows): r["row"]=i
    return rows

def telemetry(rows):
    return [{"t":r["timestamp"],"speed":r["speed_kmh"],"accel":r["acceleration_mps2"],
             "brake":r["brake"],"steer":r["steering_deg"],"remote":r["remote_command"],"event":r["event"]} for r in rows]

def analyze(rows):
    candidates=[]
    for i,r in enumerate(rows):
        prev=rows[i-1]["speed_kmh"] if i else r["speed_kmh"]
        drop=prev-r["speed_kmh"]
        severe=r["acceleration_mps2"] <= -6
        sharp=drop >= 15
        marker=r["event"].upper() in {"COLLISION","CRASH","IMPACT"}
        if severe or sharp or marker:
            score=(2 if severe else 0)+(2 if sharp else 0)+(1 if r["brake"] else 0)+(3 if marker else 0)
            reasons=[]
            if severe: reasons.append("high deceleration")
            if sharp: reasons.append("sharp speed drop")
            if r["brake"]: reasons.append("braking active")
            if marker: reasons.append("collision marker")
            candidates.append((score,i,reasons))
    accident=None
    if candidates:
        candidates.sort(key=lambda x:(-x[0],x[1]))
        _,i,reasons=candidates[0]
        accident={
            "detected":True,"index":i,"time":rows[i]["timestamp"],
            "pre_speed":rows[i-1]["speed_kmh"] if i else rows[i]["speed_kmh"],
            "post_speed":rows[min(i+1,len(rows)-1)]["speed_kmh"],
            "delta_v":(rows[i-1]["speed_kmh"] if i else rows[i]["speed_kmh"])-rows[min(i+1,len(rows)-1)]["speed_kmh"],
            "max_decel":min(x["acceleration_mps2"] for x in rows[max(0,i-2):min(len(rows),i+3)]),
            "braking":any(x["brake"] for x in rows[max(0,i-2):min(len(rows),i+3)]),
            "x":rows[i]["x"],"y":rows[i]["y"],"reasons":reasons
        }
    else: accident={"detected":False}

    remote=[]
    for i,r in enumerate(rows):
        prev=rows[i-1] if i else r
        dt=(r["timestamp"]-prev["timestamp"]) or 1.0
        speed_gain=r["speed_kmh"]-prev["speed_kmh"]
        steer_jump=abs(r["steering_deg"]-prev["steering_deg"])
        ev=r["event"].upper()
        marker=any(k in ev for k in ("REMOTE","HIJACK","INTRUSION","SPOOF","INJECT","UNAUTH"))
        unexpected=(r["acceleration_mps2"]>=5 or speed_gain/dt>=15) and not r["brake"]
        steer_anom=steer_jump>=20 and not r["brake"]
        reasons=[]
        if r["remote_command"]: reasons.append("remote-command marker")
        if marker: reasons.append("remote/hijack event marker")
        if unexpected: reasons.append("unexpected acceleration without braking")
        if steer_anom: reasons.append("abrupt steering change")
        # flag on explicit evidence, or on 2+ behavioural anomalies
        if r["remote_command"] or marker or len(reasons)>=2:
            remote.append({"index":i,"time":r["timestamp"],"before":prev["speed_kmh"],"after":r["speed_kmh"],
                           "acceleration":r["acceleration_mps2"],"reasons":reasons})
    remote_idx={e["index"] for e in remote}
    timeline=[]
    for r in rows:
        label=r["event"] or "NORMAL"
        if accident.get("detected") and r["row"]==accident["index"]: label="POSSIBLE COLLISION"
        if r["row"] in remote_idx: label="POSSIBLE REMOTE INTERVENTION"
        if label.upper()!="NORMAL": timeline.append({"time":r["timestamp"],"event":label})
    return {"rows":rows,"accident":accident,"remote":remote,"timeline":timeline,"records":len(rows),"telemetry":telemetry(rows)}

def report(result, evidence_name, evidence_hash, integrity="VERIFIED"):
    out=REPORTS/f"vehicle_forensic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=15*mm,bottomMargin=15*mm)
    s=getSampleStyleSheet()
    s.add(ParagraphStyle(name="Small2",parent=s["BodyText"],fontSize=8.5,leading=11))
    story=[Paragraph("VEHICLE FORENSIC ANALYSIS REPORT",s["Title"]),Paragraph("Simulation-based telemetry investigation",s["Heading2"]),Spacer(1,8)]
    ed=[["Evidence file",evidence_name],["Records",str(len(result["rows"]))],["SHA-256",evidence_hash],["Integrity",integrity]]
    t=Table(ed,colWidths=[45*mm,135*mm]); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.lightgrey),("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [Paragraph("1. Evidence & Integrity",s["Heading2"]),t,Spacer(1,8)]
    a=result["accident"]
    ad=[["Collision indication","DETECTED" if a["detected"] else "NOT DETECTED"]]
    if a["detected"]:
        ad += [["Estimated time",f'{a["time"]:.2f} s'],["Pre-impact speed",f'{a["pre_speed"]:.2f} km/h'],["Post-impact speed",f'{a["post_speed"]:.2f} km/h'],["Estimated delta-V",f'{a["delta_v"]:.2f} km/h'],["Maximum deceleration",f'{a["max_decel"]:.2f} m/s²'],["Braking near event","YES" if a["braking"] else "NO"],["Location",f'X={a["x"]:.2f}, Y={a["y"]:.2f}'],["Reasons","; ".join(a["reasons"])]]
    t=Table(ad,colWidths=[55*mm,125*mm]); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.lightgrey),("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [Paragraph("2. Accident Reconstruction",s["Heading2"]),t,Spacer(1,8)]
    hd=[["Remote-intervention indication","DETECTED" if result["remote"] else "NOT DETECTED"],["Flagged events",str(len(result["remote"]))]]
    for i,e in enumerate(result["remote"][:10],1):
        hd += [[f"Event {i}",f'Time {e["time"]:.2f} s; {e["before"]:.1f} to {e["after"]:.1f} km/h; {e["acceleration"]:.2f} m/s²'],["Reasons","; ".join(e["reasons"])]]
    t=Table(hd,colWidths=[55*mm,125*mm]); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.lightgrey),("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [Paragraph("3. Remote Intervention Analysis",s["Heading2"]),t,Spacer(1,8)]
    tl=[["Time (s)","Event"]]+[[f'{x["time"]:.2f}',x["event"]] for x in result["timeline"]]
    if len(tl)==1: tl.append(["-","No flagged events"])
    t=Table(tl,colWidths=[35*mm,145*mm]); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [Paragraph("4. Event Timeline",s["Heading2"]),t,Spacer(1,8)]
    story += [Paragraph("5. Interpretation & Limitations",s["Heading2"]),Paragraph("The findings are rule-based investigative indicators derived from supplied telemetry. They are not, by themselves, proof of a real-world cyberattack. Correlate them with ECU/CAN logs, network records, device logs, timestamps and physical evidence before a final forensic conclusion.",s["Small2"])]
    doc.build(story)
    return out

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/analyze")
def api_analyze():
    if "file" not in request.files: return jsonify({"error":"No CSV file supplied."}),400
    file=request.files["file"]
    if not file.filename.lower().endswith(".csv"): return jsonify({"error":"Please upload a CSV file."}),400
    safe=secure_filename(file.filename) or "evidence.csv"
    path=UPLOADS/f"upload_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{safe}"
    file.save(path)
    try:
        result=analyze(load_rows(path))
    except Exception as e:
        path.unlink(missing_ok=True)   # don't keep unreadable uploads
        return jsonify({"error":str(e)}),400
    result.pop("rows",None)
    result["evidence_name"]=file.filename
    result["sha256"]=sha256_file(path)
    result["report_url"]=None
    app.config["LAST_RESULT"]={"path":str(path),"result":result}
    return jsonify(result)

@app.post("/api/report")
def api_report():
    last=app.config.get("LAST_RESULT")
    if not last: return jsonify({"error":"Analyze evidence first."}),400
    try:
        result=analyze(load_rows(Path(last["path"])))
        now=sha256_file(last["path"])
        ok=now==last["result"]["sha256"]
        out=report(result,last["result"]["evidence_name"],last["result"]["sha256"],
                   "VERIFIED (hash re-checked at report time)" if ok else "MISMATCH - evidence file changed since import")
    except Exception as e:
        return jsonify({"error":"Report failed: "+str(e)}),500
    return send_file(out,as_attachment=True,download_name=out.name,mimetype="application/pdf")

@app.get("/api/demo/<name>")
def demo(name):
    if name not in {"accident_demo.csv","hijacking_demo.csv"}: return jsonify({"error":"Unknown demo"}),404
    path=DATA/name
    result=analyze(load_rows(path))
    result.pop("rows",None)
    result["evidence_name"]=name
    result["sha256"]=sha256_file(path)
    app.config["LAST_RESULT"]={"path":str(path),"result":result}
    return jsonify(result)

@app.errorhandler(413)
def too_large(e): return jsonify({"error":"File too large (max 25 MB)."}),413

if __name__=="__main__":
    app.run(debug=False,host="127.0.0.1",port=5000)
