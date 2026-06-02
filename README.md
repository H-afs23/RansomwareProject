# 🛡️ Ransomware Activity Detector
### Cybersecurity Course Project

---

## 📁 Project Files

| File | Purpose |
|---|---|
| `ransomware_detector.py` | Main detection engine — run this first |
| `simulate_attack.py` | Safe test simulator — run in a 2nd window |
| `dashboard.html` | Visual dashboard — open in browser |
| `ransomware_alerts.log` | Full text log (created when detector runs) |
| `events.json` | Live event data for dashboard (auto-created) |

---

## ⚙️ SETUP (One-Time)

Open Command Prompt and run:
```
pip install watchdog psutil
```

---

## 🚀 HOW TO RUN

### Step 1 — Start the Detector
Open a Command Prompt window and run:
```
python ransomware_detector.py
```
You should see: `[*] Monitoring: C:\Users\YourName\Desktop\TestFolder`

### Step 2 — Open the Dashboard
Open `dashboard.html` in your browser (Chrome or Edge recommended).
It auto-refreshes every 3 seconds.

### Step 3 — Run the Simulator (to test alerts)
Open a SECOND Command Prompt window and run:
```
python simulate_attack.py
```
Watch the detector console and dashboard light up with alerts!

### Step 4 — Stop the Detector
Press `Ctrl+C` in the detector window.

---

## 🔍 WHAT IT DETECTS

| Detection Method | How It Works |
|---|---|
| **Extension Detection** | Flags files renamed to known ransomware extensions (.locked, .enc, .crypto, etc.) |
| **Rapid Change Detection** | If 10+ file events happen in 5 seconds → Critical Alert |
| **Entropy Analysis** | Reads file bytes; encrypted data has high randomness (>7.5 bits/byte) |
| **Process Monitoring** | Checks running processes for suspicious file I/O every 5 seconds |
| **Ransom Note Detection** | Flags creation of files like "HOW_TO_DECRYPT.txt", "README.txt" |
| **Mass Delete/Rename** | Alerts on 5+ deletes or renames (ransomware behavior) |

---

## ⚠️ IMPORTANT NOTES

- The `TestFolder` on your Desktop is the watched folder
- All test files created by `simulate_attack.py` are harmless dummy text files
- No real system files are touched
- The `auto_kill_process` feature is OFF by default (for safety)

---

## 📝 FOR YOUR SUBMISSION

### Architecture Overview:
```
[File System Events]
        │
        ▼
[Watchdog Observer] ──► [FileEventHandler]
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                   ▼
    [Extension Check]   [Rapid Change]     [Entropy Check]
              │                 │                   │
              └─────────────────┴──────────────────┘
                                │
                         [AlertLogger]
                          │        │
                    [Console]   [events.json]
                                    │
                             [Dashboard HTML]

[Process Monitor Thread] ──► [psutil scan] ──► [AlertLogger]
```

### Key Concepts Used:
- **File System Monitoring** (watchdog library, Observer pattern)
- **Shannon Entropy** (information theory applied to detect encrypted data)
- **Behavioral Analysis** (rate-of-change thresholds, not signature-based)
- **Multi-threading** (process monitor runs in background)
- **Real-time Alerting** (console + log file + JSON for dashboard)
