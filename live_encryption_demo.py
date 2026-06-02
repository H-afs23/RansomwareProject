"""
============================================================
  LIVE ENCRYPTION DEMO
  Shows EXACTLY how ransomware encrypts files step by step
  Run this while ransomware_detector.py is running!
============================================================
"""

import os
import time
import base64

# ── Simple XOR encryption (same concept ransomware uses) ──
# Real ransomware uses AES-256 or RSA, but XOR shows the
# concept perfectly — the file becomes unreadable gibberish

def xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Encrypt bytes using XOR — makes file completely unreadable."""
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

# ── Folder to work in (same as detector watches) ──────────
WATCH_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "TestFolder")
DEMO_FOLDER  = os.path.join(WATCH_FOLDER, "DEMO_FILES")

# ── Encryption key (like a ransomware secret key) ─────────
SECRET_KEY = b"RANSOMWARE_KEY_2024"

def clear(): print("\n" * 2)

def pause(msg="Press ENTER to continue to next step..."):
    input(f"\n  >> {msg}")

def separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def show_file_content(filepath, label):
    """Display a file's content clearly."""
    try:
        with open(filepath, "rb") as f:
            raw = f.read()
        try:
            text = raw.decode("utf-8")
            print(f"\n  [{label}] — READABLE TEXT:")
            print("  " + "-" * 40)
            for line in text.splitlines()[:6]:
                print(f"  {line}")
            print("  " + "-" * 40)
        except UnicodeDecodeError:
            print(f"\n  [{label}] — ENCRYPTED (UNREADABLE BINARY):")
            print("  " + "-" * 40)
            hex_preview = raw[:48].hex()
            print(f"  HEX: {hex_preview}...")
            print(f"  This is what encrypted data looks like — pure gibberish!")
            print("  " + "-" * 40)
    except FileNotFoundError:
        print(f"  [!] File not found: {filepath}")

# ══════════════════════════════════════════════════════════
#  MAIN DEMO
# ══════════════════════════════════════════════════════════

def main():
    separator("LIVE RANSOMWARE ENCRYPTION DEMO")
    print("""
  This demo shows EXACTLY what ransomware does:
  
  STEP 1 — Create a normal file with readable content
  STEP 2 — Encrypt the file (content becomes unreadable)
  STEP 3 — Rename with ransomware extension (.locked)
  STEP 4 — Drop a ransom note
  STEP 5 — Show what SAME NAME trigger looks like
  STEP 6 — Clean up everything
  
  Make sure ransomware_detector.py is running in another
  window so you can see alerts fire in real time!
    """)

    pause("START THE DEMO")

    # Create demo folder
    os.makedirs(DEMO_FOLDER, exist_ok=True)

    # ──────────────────────────────────────────────────────
    #  STEP 1: Create normal readable files
    # ──────────────────────────────────────────────────────
    separator("STEP 1: Creating Normal User Files")
    print("""
  Imagine these are YOUR files on your computer:
  - A university assignment
  - Personal notes
  - An important letter
  
  Before ransomware: everything is readable and normal.
    """)

    files = {
        "university_assignment.txt": """University of Engineering
Subject: Cybersecurity
Assignment Title: Network Security Analysis

Introduction:
This assignment covers the fundamentals of network security
including firewalls, intrusion detection systems, and VPNs.

The goal is to analyze threats and propose countermeasures.
Student: Hafsa Irfan (230942)""",

        "personal_notes.txt": """My Personal Notes - May 2026
================================
- Buy groceries on the way home
- Study for cybersecurity exam
- Call mom at 7pm
- Submit project by tomorrow
- Password for email: (stored securely elsewhere)
This is my private data. Nobody else should read this.""",

        "important_letter.txt": """Dear Sir Ayaaz,

I am writing to request an extension on the project deadline.
Due to unforeseen circumstances, we were unable to complete
the full implementation on time.

We have completed 90% of the project and only need 2 more days.

Regards,
Hafsa Irfan & Humdia Amjad
Cybersecurity Course - 2026"""
    }

    created = []
    for filename, content in files.items():
        fpath = os.path.join(DEMO_FOLDER, filename)
        with open(fpath, "w") as f:
            f.write(content)
        created.append(fpath)
        print(f"  [+] Created: {filename}")
        time.sleep(0.3)

    print("\n  All files are normal and readable right now.")
    print("  Let's read one to confirm:")
    show_file_content(created[0], "university_assignment.txt  BEFORE encryption")

    pause("STEP 2 — Now simulate ransomware ENCRYPTING these files")

    # ──────────────────────────────────────────────────────
    #  STEP 2: Encrypt each file
    # ──────────────────────────────────────────────────────
    separator("STEP 2: Ransomware Encrypts the Files")
    print("""
  Real ransomware uses AES-256 encryption.
  We use XOR encryption here — same concept, simpler code.
  
  Encryption = scramble the bytes using a secret KEY
  Only someone with the KEY can unscramble (decrypt) it.
  
  Ransomware keeps the KEY and demands money to give it to you.
    """)

    encrypted_files = []
    for fpath in created:
        filename = os.path.basename(fpath)
        print(f"\n  Encrypting: {filename}...")

        # Read original
        with open(fpath, "rb") as f:
            original_data = f.read()

        # Encrypt
        encrypted_data = xor_encrypt(original_data, SECRET_KEY)

        # Write encrypted content BACK to same file
        with open(fpath, "wb") as f:
            f.write(encrypted_data)

        encrypted_files.append(fpath)
        print(f"  [!] File is now encrypted — content destroyed!")
        time.sleep(0.4)

    print("\n  Now let's READ the same file — watch what happens:")
    show_file_content(created[0], "university_assignment.txt  AFTER encryption")

    print("""
  See the difference?
  BEFORE: Normal readable text about your assignment
  AFTER:  Random hex gibberish — completely unreadable!
  
  Your data is GONE unless you have the decryption key.
    """)

    pause("STEP 3 — Now rename files with ransomware extension (THIS TRIGGERS THE DETECTOR!)")

    # ──────────────────────────────────────────────────────
    #  STEP 3: Rename with ransomware extensions
    # ──────────────────────────────────────────────────────
    separator("STEP 3: Renaming Files with Ransomware Extensions")
    print("""
  After encrypting, ransomware renames files to signal
  they are encrypted and belong to THIS ransomware family.
  
  Examples:
    photo.jpg        -->  photo.jpg.locked
    document.docx   -->  document.docx.wcry
    notes.txt        -->  notes.txt.encrypted
  
  THIS IS WHAT TRIGGERS THE DETECTOR'S EXTENSION ALERT!
  Watch the detector window right now...
    """)

    extensions = [".locked", ".wcry", ".encrypted"]
    renamed_files = []

    for i, fpath in enumerate(encrypted_files):
        ext   = extensions[i % len(extensions)]
        new_path = fpath + ext
        os.rename(fpath, new_path)
        renamed_files.append(new_path)

        old_name = os.path.basename(fpath)
        new_name = os.path.basename(new_path)
        print(f"  RENAMED: {old_name}")
        print(f"       --> {new_name}  <<<  DETECTOR SHOULD FIRE NOW!")
        print()
        time.sleep(1.5)  # slow so user can watch alerts appear

    print("""
  Check your detector window!
  You should see CRITICAL alerts for each renamed file.
  The detector recognized the .locked / .wcry extensions
  from its database of 50+ known ransomware extensions.
    """)

    pause("STEP 4 — Drop a ransom note (another alert!)")

    # ──────────────────────────────────────────────────────
    #  STEP 4: Drop ransom note
    # ──────────────────────────────────────────────────────
    separator("STEP 4: Dropping the Ransom Note")
    print("""
  Every real ransomware drops a text file explaining
  what happened and how to pay to get files back.
  
  Common names: HOW_TO_DECRYPT.txt, README.txt, !HELP!.txt
  
  Our detector knows these filenames — watch for the alert!
    """)

    note_path = os.path.join(DEMO_FOLDER, "HOW_TO_DECRYPT.txt")
    ransom_note = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                  YOUR FILES ARE ENCRYPTED
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

All your important files have been encrypted using
military-grade AES-256 encryption.

YOUR FILES INCLUDE:
 - university_assignment.txt
 - personal_notes.txt
 - important_letter.txt

To decrypt your files, you must pay 0.5 Bitcoin to:
  Wallet: 1A2B3C4D5E6F7G8H9I0J (DO NOT CONTACT POLICE)

After payment, email: decrypt@darkweb.onion
You have 72 HOURS before the key is permanently deleted.

--- THIS IS A DEMONSTRATION FOR EDUCATIONAL PURPOSES ---
--- NO REAL FILES WERE HARMED IN THIS DEMONSTRATION  ---
"""

    with open(note_path, "w") as f:
        f.write(ransom_note)

    print(f"  [!] Ransom note dropped: HOW_TO_DECRYPT.txt")
    print(f"      --> Detector should fire CRITICAL: RANSOM NOTE DETECTED!")

    time.sleep(1)
    print("\n  Content of the ransom note:")
    print("  " + "-" * 50)
    with open(note_path, "r") as f:
        for line in f.read().splitlines()[:12]:
            print(f"  {line}")
    print("  " + "-" * 50)

    pause("STEP 5 — Show the SAME NAME TRIGGER (what sir asked about!)")

    # ──────────────────────────────────────────────────────
    #  STEP 5: Same name trigger demo
    # ──────────────────────────────────────────────────────
    separator("STEP 5: Same Name Trigger — Sir's Question!")
    print("""
  Sir's question: "If we save a file with the same name,
  will it trigger an alert?"
  
  ANSWER: YES — but only if the name matches a ransomware
  extension or a ransom note pattern.
  
  Let's prove it with 3 tests:
    """)

    # Test A: Normal filename — no alert
    print("  TEST A: Save a file with a NORMAL name")
    print("          --> Should NOT trigger any alert")
    normal_path = os.path.join(DEMO_FOLDER, "my_homework.txt")
    with open(normal_path, "w") as f:
        f.write("This is a normal file. Nothing suspicious here.")
    print(f"  [+] Created: my_homework.txt")
    print(f"      (Check detector — only an INFO log, no alert)")
    time.sleep(2)

    # Test B: File with ransomware extension — ALERT!
    print("\n  TEST B: Save a file with a RANSOMWARE EXTENSION")
    print("          --> SHOULD trigger CRITICAL alert!")
    locked_path = os.path.join(DEMO_FOLDER, "my_homework.txt.locked")
    with open(locked_path, "wb") as f:
        f.write(b"\x9f\x3a\x7c\x12\x45\xab\xde\xf0\x11\x22\x33\x44")
    print(f"  [!!!] Created: my_homework.txt.locked")
    print(f"        --> CRITICAL alert should fire right now!")
    print(f"        The .locked extension is in our ransomware database!")
    time.sleep(2)

    # Test C: Ransom note filename — ALERT!
    print("\n  TEST C: Save a file named like a ransom note")
    print("          --> SHOULD trigger CRITICAL alert!")
    readme_path = os.path.join(DEMO_FOLDER, "README.txt")
    with open(readme_path, "w") as f:
        f.write("YOUR FILES ARE LOCKED. PAY NOW.")
    print(f"  [!!!] Created: README.txt")
    print(f"        --> CRITICAL alert: RANSOM NOTE DETECTED!")
    time.sleep(2)

    print("""
  SUMMARY OF TEST RESULTS:
  ─────────────────────────────────────────────────────
  my_homework.txt         --> INFO only (no alert)  ✓
  my_homework.txt.locked  --> CRITICAL ALERT!       ✓
  README.txt              --> CRITICAL ALERT!       ✓
  ─────────────────────────────────────────────────────
  
  So to answer Sir's question directly:
  
  "If you save ANY file with a ransomware extension
   (.locked, .encrypted, .wcry, etc.) — even if you
   create it manually — the detector will fire a
   CRITICAL alert immediately."
  
  "The detector doesn't care WHO created the file.
   It only looks at the FILE EXTENSION and FILENAME.
   This is exactly how behavioral detection works!"
    """)

    pause("STEP 6 — Clean up all demo files")

    # ──────────────────────────────────────────────────────
    #  STEP 6: Cleanup
    # ──────────────────────────────────────────────────────
    separator("STEP 6: Cleaning Up Demo Files")

    import shutil
    try:
        shutil.rmtree(DEMO_FOLDER)
        print(f"  [+] Removed demo folder and all files inside.")
    except Exception as e:
        print(f"  [!] Could not auto-remove: {e}")
        print(f"      Please manually delete: {DEMO_FOLDER}")

    separator("DEMO COMPLETE!")
    print("""
  WHAT YOU JUST SAW:
  
  1. Normal files created   --> Detector logs INFO (no alert)
  2. Files encrypted        --> Content becomes unreadable gibberish
  3. Files renamed .locked  --> CRITICAL: extension detected!
  4. Ransom note dropped    --> CRITICAL: ransom note detected!
  5. Same-name test         --> Proved any .locked file triggers alert
  6. Normal name test       --> Proved normal files do NOT trigger
  
  KEY POINT FOR SIR:
  ─────────────────────────────────────────────────────
  The detector uses BEHAVIORAL analysis, not signatures.
  It doesn't need to know WHICH ransomware is running.
  ANY file that behaves like ransomware gets flagged —
  including files you create manually with those extensions!
  ─────────────────────────────────────────────────────
    """)


if __name__ == "__main__":
    main()
