"""
============================================================
  RANSOMWARE SIMULATOR — FOR TESTING ONLY
  
  This script SAFELY simulates ransomware behavior
  in a controlled test folder.
  
  ⚠️  Run this WHILE the detector is running to see alerts!
  ⚠️  This only creates/renames dummy files — no real harm.
============================================================
"""

import os
import time
import random

# ── Test folder (must match detector's watch_folder) ──────
TEST_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "TestFolder")

# ── Ransomware extensions to simulate ────────────────────
FAKE_RANSOM_EXTENSIONS = [".locked", ".enc", ".wcry", ".crypto"]

def simulate_ransomware():
    print("=" * 55)
    print("  ⚠️  RANSOMWARE SIMULATOR (Safe Test Mode)")
    print("  This creates harmless dummy files to test")
    print("  the detector. No real files are harmed.")
    print("=" * 55)

    if not os.path.exists(TEST_FOLDER):
        os.makedirs(TEST_FOLDER)

    # ── Step 1: Create normal dummy files ─────────────────
    print("\n[Step 1] Creating 10 fake 'user' files...")
    fake_files = []
    for i in range(10):
        fname = f"document_{i+1}.txt"
        fpath = os.path.join(TEST_FOLDER, fname)
        with open(fpath, "w") as f:
            f.write(f"This is fake user document #{i+1}.\n" * 50)
        fake_files.append(fpath)
        print(f"  Created: {fname}")
        time.sleep(0.2)

    time.sleep(1)

    # ── Step 2: Simulate rapid modifications ──────────────
    print("\n[Step 2] Simulating rapid file modifications...")
    print("         (This should trigger rapid-change alert!)")
    for fpath in fake_files:
        with open(fpath, "ab") as f:
            # Write random bytes (simulates encryption output)
            f.write(os.urandom(512))
        print(f"  Modified: {os.path.basename(fpath)}")
        time.sleep(0.1)  # Very fast = suspicious

    time.sleep(1)

    # ── Step 3: Rename files with ransomware extension ────
    print("\n[Step 3] Renaming files with ransomware extensions...")
    print("         (This should trigger extension alert!)")
    renamed = []
    for fpath in fake_files:
        ext = random.choice(FAKE_RANSOM_EXTENSIONS)
        new_path = fpath.replace(".txt", ext)
        os.rename(fpath, new_path)
        renamed.append(new_path)
        print(f"  Renamed: {os.path.basename(fpath)} → {os.path.basename(new_path)}")
        time.sleep(0.3)

    time.sleep(1)

    # ── Step 4: Drop a fake ransom note ───────────────────
    print("\n[Step 4] Dropping a ransom note...")
    note_path = os.path.join(TEST_FOLDER, "HOW_TO_DECRYPT.txt")
    with open(note_path, "w") as f:
        f.write("YOUR FILES HAVE BEEN ENCRYPTED (simulated)\n")
        f.write("This is a test for a cybersecurity course.\n")
        f.write("No real files were harmed.\n")
    print(f"  Created: HOW_TO_DECRYPT.txt")

    time.sleep(1)

    # ── Step 5: Clean up ─────────────────────────────────
    print("\n[Step 5] Cleaning up test files...")
    for fpath in renamed:
        try:
            os.remove(fpath)
        except FileNotFoundError:
            pass
    try:
        os.remove(note_path)
    except FileNotFoundError:
        pass
    print("  All test files removed.")

    print("\n" + "=" * 55)
    print("  Simulation complete! Check the detector console")
    print("  and dashboard.html for logged alerts.")
    print("=" * 55)


if __name__ == "__main__":
    simulate_ransomware()
