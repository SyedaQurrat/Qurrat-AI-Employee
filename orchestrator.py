import time
import os
import subprocess
import sys
from datetime import datetime

# --- CONFIGURATION ---
# The folders we need to monitor for counts
FOLDERS = {
    "Needs_Action": "Needs_Action",
    "Plans": "Plans",
    "Done": "Done",
    "Pending_Approval": "Pending_Approval"
}
DASHBOARD_FILE = "Dashboard.md"

def get_md_count(folder_path):
    """
    Counts how many .md files are in a specific folder.
    """
    if not os.path.exists(folder_path):
        return 0
    # List all files and filter for those ending with .md
    files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    return len(files)

def update_dashboard(counts):
    """
    Updates Dashboard.md with the latest counts and a timestamp.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create the new dashboard content
    content = f"""# 📊 Qurrat-AI Executive Dashboard

## 📈 Live Vault Status
| Folder | Status | File Count |
| :--- | :---: | :--- |
| **Needs Action** | 🚨 | {counts['Needs_Action']} |
| **Plans** | 🚧 | {counts['Plans']} |
| **Pending Approval** | ⏳ | {counts['Pending_Approval']} |
| **Done** | ✅ | {counts['Done']} |

---

## 🕒 Last System Pulse
- **Date/Time:** {timestamp}
- **Status:** All systems operational 🚀

---
*This dashboard is automatically updated every 60 seconds by orchestrator.py*
"""
    try:
        with open(DASHBOARD_FILE, "w") as f:
            f.write(content)
        # print(f"[{timestamp}] Dashboard.md updated successfully.")
    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")

def main():
    print("🤖 Qurrat-AI Orchestrator starting...")
    
    # 1. Start file_watcher.py as a background process
    try:
        print("📁 Starting file_watcher.py in the background...")
        # Use sys.executable to ensure we use the same python version
        watcher_process = subprocess.Popen([sys.executable, "file_watcher.py"])
    except Exception as e:
        print(f"❌ Failed to start file_watcher.py: {e}")
        return

    try:
        while True:
            # 2. Scan folders and count .md files
            current_counts = {}
            for key, folder in FOLDERS.items():
                current_counts[key] = get_md_count(folder)
            
            # 3. Update Dashboard.md
            update_dashboard(current_counts)
            
            # 4. Print status log
            log_time = datetime.now().strftime("%H:%M:%S")
            print(f"[{log_time}] Status: {current_counts['Needs_Action']} Pending, {current_counts['Done']} Done.")
            
            # 5. Wait for 60 seconds
            time.sleep(60)
            
    except KeyboardInterrupt:
        # 6. Handle Ctrl+C gracefully
        print("\n🛑 Orchestrator shutting down...")
        print("🔌 Stopping file_watcher.py...")
        watcher_process.terminate() # Safely stop the background process
        watcher_process.wait()      # Wait for it to fully exit
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
