import json
import os
import time
import threading
from datetime import datetime

from flask import Flask

app = Flask(__name__)

# Track when the dashboard started
start_time = time.time()

# File paths (same directory as this script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
LOG_FILE = os.path.join(BASE_DIR, "events.log")


def read_state():
    """Read current door state from state.json."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"state": "UNKNOWN", "last_updated": "N/A", "last_event": "N/A"}


def read_logs(n=20):
    """Read last N lines from events.log."""
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        return [line.strip() for line in lines[-n:]]
    except Exception:
        return []


def count_events_today():
    """Count total events and denied attempts today."""
    today = datetime.now().strftime("%d/%m/%Y")
    total = 0
    denied = 0
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                if line.startswith(today):
                    total += 1
                    if "denied" in line.lower() or "wrong" in line.lower():
                        denied += 1
    except Exception:
        pass
    return total, denied


def format_uptime(seconds):
    """Format uptime in human-readable form."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return "{}h {}m {}s".format(hours, minutes, secs)
    elif minutes > 0:
        return "{}m {}s".format(minutes, secs)
    return "{}s".format(secs)


@app.route("/")
def index():
    state = read_state()
    logs = read_logs(20)
    total_today, denied_today = count_events_today()
    uptime = format_uptime(time.time() - start_time)

    # State color mapping
    state_colors = {
        "LOCKED": "#e74c3c",
        "OPEN": "#2ecc71",
        "PENDING_APPROVAL": "#f39c12",
        "OPEN_EXIT": "#3498db",
        "UNKNOWN": "#95a5a6"
    }
    state_color = state_colors.get(state.get("state", "UNKNOWN"), "#95a5a6")

    # Build log rows
    log_rows = ""
    for line in reversed(logs):
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        log_rows += "<tr><td>{}</td></tr>\n".format(escaped)

    html = """<!DOCTYPE html>
<html>
<head>
<title>Security Door Dashboard</title>
<meta http-equiv="refresh" content="5">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #1a1a2e;
    color: #eee;
    font-family: 'Courier New', monospace;
    padding: 20px;
  }}
  h1 {{
    text-align: center;
    color: #e94560;
    margin-bottom: 20px;
    font-size: 1.8em;
  }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  .card {{
    background: #16213e;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }}
  .card h2 {{
    color: #e94560;
    margin-bottom: 15px;
    font-size: 1.2em;
    border-bottom: 1px solid #0f3460;
    padding-bottom: 8px;
  }}
  .status-badge {{
    display: inline-block;
    padding: 8px 20px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 1.4em;
    color: #fff;
    background: {state_color};
  }}
  .info-row {{
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #0f3460;
  }}
  .info-label {{ color: #a0a0a0; }}
  .info-value {{ color: #eee; font-weight: bold; }}
  .stats-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 15px;
  }}
  .stat-box {{
    background: #0f3460;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
  }}
  .stat-number {{
    font-size: 2em;
    font-weight: bold;
    color: #e94560;
  }}
  .stat-label {{ color: #a0a0a0; margin-top: 5px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  td {{
    padding: 6px 10px;
    border-bottom: 1px solid #0f3460;
    font-size: 0.85em;
  }}
  tr:hover {{ background: #0f3460; }}
  .footer {{
    text-align: center;
    color: #555;
    margin-top: 20px;
    font-size: 0.8em;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>Security Door System v6</h1>

  <div class="card">
    <h2>Door Status</h2>
    <div style="text-align:center; margin: 15px 0;">
      <span class="status-badge">{state}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Last Updated</span>
      <span class="info-value">{last_updated}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Last Event</span>
      <span class="info-value">{last_event}</span>
    </div>
  </div>

  <div class="card">
    <h2>Statistics (Today)</h2>
    <div class="stats-grid">
      <div class="stat-box">
        <div class="stat-number">{total_today}</div>
        <div class="stat-label">Total Events</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">{denied_today}</div>
        <div class="stat-label">Denied Attempts</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">{uptime}</div>
        <div class="stat-label">Uptime</div>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>Recent Events (Last 20)</h2>
    <table>
      {log_rows}
    </table>
  </div>

  <div class="footer">
    Auto-refreshes every 5 seconds | Security Door System v6
  </div>
</div>
</body>
</html>""".format(
        state=state.get("state", "UNKNOWN"),
        state_color=state_color,
        last_updated=state.get("last_updated", "N/A"),
        last_event=state.get("last_event", "N/A"),
        total_today=total_today,
        denied_today=denied_today,
        uptime=uptime,
        log_rows=log_rows
    )

    return html


def start_dashboard(port=5000):
    """Start the Flask dashboard in a daemon thread."""
    def run():
        # Disable Flask request logging to keep console clean
        import logging
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print("[DASHBOARD] Web dashboard started on port {}".format(port))
