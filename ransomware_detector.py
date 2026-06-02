"""
============================================================
  RANSOMWARE ACTIVITY DETECTOR
  Cybersecurity Course Project
  Detects ransomware behavior via file & process monitoring
============================================================
"""

import os
import time
import json
import hashlib
import threading
import subprocess
from datetime import datetime
from collections import defaultdict

# ── Try importing optional libraries ──────────────────────
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[WARNING] psutil not installed. Process monitoring disabled.")
    print("          Run: pip install psutil\n")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("[WARNING] watchdog not installed. Using fallback file scanner.")
    print("          Run: pip install watchdog\n")


# ══════════════════════════════════════════════════════════
#  CONFIGURATION — Edit these settings as needed
# ══════════════════════════════════════════════════════════

CONFIG = {
    # Folder to monitor for suspicious file activity
    "watch_folder": os.path.join(os.path.expanduser("~"), "Desktop", "TestFolder"),

    # How many file changes in a short time = suspicious
    "rapid_change_threshold": 10,       # number of file events
    "rapid_change_window_sec": 5,       # within this many seconds

    # How many renames/deletes = suspicious
    "rename_threshold": 5,
    "delete_threshold": 5,

    # Scan interval for fallback scanner (seconds)
    "scan_interval_sec": 3,

    # Log file output
    "log_file": "ransomware_alerts.log",

    # JSON events file (for the dashboard)
    "events_file": "events.json",

    # Whether to show process info (requires psutil)
    "monitor_processes": True,

    # Whether to auto-terminate suspicious processes
    # ⚠️  Set to True only in a controlled lab environment!
    "auto_kill_process": False,
}

# ══════════════════════════════════════════════════════════
#  KNOWN RANSOMWARE FILE EXTENSIONS
#  (These are real extensions used by ransomware families)
# ══════════════════════════════════════════════════════════

RANSOMWARE_EXTENSIONS = {
    # Generic ransom extensions
    ".locked", ".lock", ".encrypt", ".encrypted",
    ".enc", ".crypto", ".crypt", ".crypted",
    ".aes", ".aes256", ".rsa", ".rsa2048",

    # Named ransomware families
    ".wannacry", ".wcry", ".wncry",         # WannaCry
    ".locky", ".zepto", ".odin",            # Locky family
    ".cerber", ".cerber2", ".cerber3",      # Cerber
    ".dharma", ".cezar", ".java",           # Dharma
    ".ryuk",                                 # Ryuk
    ".maze",                                 # Maze
    ".revil", ".sodinokibi",                # REvil
    ".darkside",                             # DarkSide
    ".conti",                                # Conti
    ".phobos",                               # Phobos
    ".zzzzz", ".shit", ".thor",             # Various
    ".fun", ".helpme", ".pays",
    ".xtbl", ".breaking_bad",
    ".good", ".keybtc@inbox_com",
    ".ha3", ".vvv", ".exx", ".xyz",
    ".zzz", ".micro", ".ttt", ".mp3",       # CryptoWall
    ".xxx", ".ttt", ".yyy",
}

# ══════════════════════════════════════════════════════════
#  SUSPICIOUS RANSOM NOTE FILENAMES
# ══════════════════════════════════════════════════════════

RANSOM_NOTE_NAMES = {
    "readme.txt", "read_me.txt", "how_to_decrypt.txt",
    "decrypt_instructions.txt", "how_to_recover_files.txt",
    "ransom_note.txt", "your_files_are_encrypted.txt",
    "!!!_important_!!!.txt", "!!!help!!!.txt",
    "restore_files.txt", "help_recover_files.html",
    "decrypt_files.html", "recovery.txt",
    "@please_read_me@.txt", "@warning.txt",
    "message.txt", "instructions.txt",
}


# ══════════════════════════════════════════════════════════
#  ALERT LOGGER
# ══════════════════════════════════════════════════════════

class AlertLogger:
    """Handles logging alerts to console, file, and JSON."""

    def __init__(self):
        self.alerts = []
        self.events = []
        self.lock = threading.Lock()

        # Clear old log file
        with open(CONFIG["log_file"], "w", encoding="utf-8") as f:
            f.write(f"{'='*60}\n")
            f.write(f"  RANSOMWARE DETECTOR LOG\n")
            f.write(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")

    def log(self, level, message, details=None):
        """Log an event at a given severity level."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Console colors (Windows-compatible using plain symbols)
        icons = {"INFO": "[*]", "WARNING": "[!]", "CRITICAL": "[!!!]"}
        icon = icons.get(level, "[?]")

        line = f"{icon} [{timestamp}] {level}: {message}"
        print(line)
        if details:
            print(f"    Details: {details}")

        # Write to log file
        with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
            f.write(line + "\n")
            if details:
                f.write(f"    Details: {details}\n")

        # Store event for dashboard
        event = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "details": details or "",
        }
        with self.lock:
            self.events.append(event)
            self._save_events()

    def _save_events(self):
        """Save events to JSON file for the dashboard."""
        try:
            with open(CONFIG["events_file"], "w") as f:
                json.dump(self.events, f, indent=2)
        except Exception:
            pass

    def alert_count(self):
        return {"INFO": 0, "WARNING": 0, "CRITICAL": 0,
                **{e["level"]: sum(1 for x in self.events if x["level"] == e["level"])
                   for e in self.events}}


# ══════════════════════════════════════════════════════════
#  DETECTION ENGINE
# ══════════════════════════════════════════════════════════

class RansomwareDetector:
    """Core detection logic for ransomware behavior."""

    def __init__(self, logger):
        self.logger = logger
        self.event_times = []          # Timestamps of recent file events
        self.rename_count = 0
        self.delete_count = 0
        self.flagged_processes = set()
        self.lock = threading.Lock()

        self.logger.log("INFO", "Detector initialized",
                        f"Watching: {CONFIG['watch_folder']}")

    # ── Extension Check ──────────────────────────────────

    def check_extension(self, filepath):
        """Check if a file has a known ransomware extension."""
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if ext in RANSOMWARE_EXTENSIONS:
            self.logger.log(
                "CRITICAL",
                f"RANSOMWARE EXTENSION DETECTED: {ext}",
                f"File: {filepath}"
            )
            return True

        # Check for ransom note filenames
        filename = os.path.basename(filepath).lower()
        if filename in RANSOM_NOTE_NAMES:
            self.logger.log(
                "CRITICAL",
                f"RANSOM NOTE DETECTED: {filename}",
                f"Path: {filepath}"
            )
            return True

        return False

    # ── Rapid Change Detection ───────────────────────────

    def record_event(self, event_type):
        """Track file events and alert if too many happen too fast."""
        now = time.time()
        window = CONFIG["rapid_change_window_sec"]

        with self.lock:
            self.event_times.append(now)
            # Remove events outside the time window
            self.event_times = [t for t in self.event_times if now - t <= window]

            count = len(self.event_times)
            threshold = CONFIG["rapid_change_threshold"]

            if count >= threshold:
                self.logger.log(
                    "CRITICAL",
                    f"RAPID FILE ACTIVITY: {count} changes in {window}s",
                    "This matches mass-encryption behavior of ransomware!"
                )
                self.event_times = []  # Reset to avoid spam

            # Track specific event types
            if event_type == "renamed":
                self.rename_count += 1
                if self.rename_count >= CONFIG["rename_threshold"]:
                    self.logger.log(
                        "WARNING",
                        f"MASS RENAME DETECTED: {self.rename_count} renames",
                        "Ransomware often renames files after encryption."
                    )
                    self.rename_count = 0

            elif event_type == "deleted":
                self.delete_count += 1
                if self.delete_count >= CONFIG["delete_threshold"]:
                    self.logger.log(
                        "WARNING",
                        f"MASS DELETION DETECTED: {self.delete_count} deletes",
                        "Ransomware deletes originals after encrypting them."
                    )
                    self.delete_count = 0

    # ── Process Monitor ──────────────────────────────────

    def check_processes(self):
        """Monitor running processes for suspicious file I/O."""
        if not PSUTIL_AVAILABLE or not CONFIG["monitor_processes"]:
            return

        try:
            for proc in psutil.process_iter(["pid", "name", "exe", "open_files"]):
                try:
                    pid = proc.info["pid"]
                    name = proc.info["name"] or "unknown"

                    if pid in self.flagged_processes:
                        continue  # Already flagged

                    # Check open files for ransomware extensions
                    open_files = proc.open_files()
                    for f in open_files:
                        _, ext = os.path.splitext(f.path)
                        if ext.lower() in RANSOMWARE_EXTENSIONS:
                            self.flagged_processes.add(pid)
                            self.logger.log(
                                "CRITICAL",
                                f"SUSPICIOUS PROCESS: {name} (PID {pid})",
                                f"Accessing ransomware-extension file: {f.path}"
                            )
                            if CONFIG["auto_kill_process"]:
                                self._kill_process(proc, name, pid)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            pass  # Process list errors are non-fatal

    def _kill_process(self, proc, name, pid):
        """Terminate a suspicious process (lab use only)."""
        try:
            proc.kill()
            self.logger.log(
                "CRITICAL",
                f"PROCESS TERMINATED: {name} (PID {pid})",
                "Auto-kill triggered due to ransomware behavior."
            )
        except Exception as e:
            self.logger.log("WARNING", f"Could not kill process {name}: {e}")

    # ── Entropy Check (Advanced) ─────────────────────────

    def check_entropy(self, filepath):
        """
        High entropy = encrypted/compressed data.
        Ransomware produces near-maximum entropy files.
        Shannon entropy > 7.5 bits/byte is suspicious.
        """
        try:
            if not os.path.isfile(filepath):
                return
            if os.path.getsize(filepath) < 512:
                return  # Too small to measure

            with open(filepath, "rb") as f:
                data = f.read(65536)  # Read first 64KB

            # Calculate Shannon entropy
            byte_counts = [0] * 256
            for byte in data:
                byte_counts[byte] += 1

            entropy = 0.0
            length = len(data)
            for count in byte_counts:
                if count > 0:
                    p = count / length
                    import math
                    entropy -= p * math.log2(p)

            if entropy > 7.5:
                self.logger.log(
                    "WARNING",
                    f"HIGH ENTROPY FILE: {os.path.basename(filepath)}",
                    f"Entropy={entropy:.2f} bits/byte (>7.5 = likely encrypted). "
                    f"Path: {filepath}"
                )

        except (PermissionError, OSError):
            pass


# ══════════════════════════════════════════════════════════
#  FILE SYSTEM WATCHER (uses watchdog library)
# ══════════════════════════════════════════════════════════

if WATCHDOG_AVAILABLE:

    class FileEventHandler(FileSystemEventHandler):
        """Handles file system events from watchdog."""

        def __init__(self, detector):
            self.detector = detector

        def on_created(self, event):
            if event.is_directory:
                return
            path = event.src_path
            self.detector.logger.log("INFO", f"File created: {os.path.basename(path)}")
            self.detector.check_extension(path)
            self.detector.record_event("created")
            self.detector.check_entropy(path)

        def on_modified(self, event):
            if event.is_directory:
                return
            path = event.src_path
            self.detector.record_event("modified")
            self.detector.check_entropy(path)

        def on_deleted(self, event):
            if event.is_directory:
                return
            path = event.src_path
            self.detector.logger.log("INFO", f"File deleted: {os.path.basename(path)}")
            self.detector.record_event("deleted")

        def on_moved(self, event):
            if event.is_directory:
                return
            self.detector.logger.log(
                "INFO",
                f"File renamed: {os.path.basename(event.src_path)} --> {os.path.basename(event.dest_path)}"
            )
            self.detector.check_extension(event.dest_path)
            self.detector.record_event("renamed")


# ══════════════════════════════════════════════════════════
#  FALLBACK SCANNER (when watchdog is not available)
# ══════════════════════════════════════════════════════════

class FallbackScanner:
    """Periodically scans a folder for ransomware indicators."""

    def __init__(self, detector):
        self.detector = detector
        self.known_files = {}
        self._snapshot()

    def _snapshot(self):
        """Take a snapshot of current files and their sizes."""
        folder = CONFIG["watch_folder"]
        if not os.path.exists(folder):
            return
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            try:
                self.known_files[fpath] = os.path.getsize(fpath)
            except OSError:
                pass

    def scan(self):
        """Compare current state to snapshot and report changes."""
        folder = CONFIG["watch_folder"]
        if not os.path.exists(folder):
            return

        current = {}
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            try:
                current[fpath] = os.path.getsize(fpath)
            except OSError:
                pass

        # New files
        for fpath in current:
            if fpath not in self.known_files:
                self.detector.logger.log("INFO", f"New file: {os.path.basename(fpath)}")
                self.detector.check_extension(fpath)
                self.detector.record_event("created")
                self.detector.check_entropy(fpath)

        # Deleted files
        for fpath in self.known_files:
            if fpath not in current:
                self.detector.logger.log("INFO", f"Deleted: {os.path.basename(fpath)}")
                self.detector.record_event("deleted")

        # Modified files
        for fpath in current:
            if fpath in self.known_files and current[fpath] != self.known_files[fpath]:
                self.detector.record_event("modified")
                self.detector.check_entropy(fpath)

        self.known_files = current


# ══════════════════════════════════════════════════════════
#  MAIN — Entry Point
# ══════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  🛡️  RANSOMWARE ACTIVITY DETECTOR")
    print("  Cybersecurity Course Project")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Create watch folder if it doesn't exist
    watch_folder = CONFIG["watch_folder"]
    if not os.path.exists(watch_folder):
        os.makedirs(watch_folder)
        print(f"\n[*] Created test folder: {watch_folder}")

    print(f"\n[*] Monitoring: {watch_folder}")
    print(f"[*] Log file:   {CONFIG['log_file']}")
    print(f"[*] Dashboard:  Open dashboard.html in your browser")
    print(f"\n[*] Press Ctrl+C to stop\n")
    print("-" * 60)

    # Initialize components
    logger = AlertLogger()
    detector = RansomwareDetector(logger)

    # Start process monitor in background
    def process_monitor_loop():
        while True:
            detector.check_processes()
            time.sleep(5)

    if PSUTIL_AVAILABLE and CONFIG["monitor_processes"]:
        t = threading.Thread(target=process_monitor_loop, daemon=True)
        t.start()
        logger.log("INFO", "Process monitor started (checking every 5 seconds)")

    # Start file watcher
    if WATCHDOG_AVAILABLE:
        logger.log("INFO", "Using real-time file watcher (watchdog)")
        event_handler = FileEventHandler(detector)
        observer = Observer()
        observer.schedule(event_handler, watch_folder, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()

    else:
        logger.log("INFO", f"Using fallback scanner (every {CONFIG['scan_interval_sec']}s)")
        scanner = FallbackScanner(detector)
        try:
            while True:
                scanner.scan()
                time.sleep(CONFIG["scan_interval_sec"])
        except KeyboardInterrupt:
            pass

    print("\n" + "=" * 60)
    print("  Detector stopped. Check ransomware_alerts.log for full report.")
    print("=" * 60)


if __name__ == "__main__":
    main()
