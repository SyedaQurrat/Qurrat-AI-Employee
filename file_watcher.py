import time
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
# Define the directories we are working with
# Using relative paths based on the script's location in the AI_Employee_Vault root
WATCH_DIR = "Inbox"
ACTION_DIR = "Needs_Action"

# --- TASK GENERATOR ---
def create_task_file(file_path):
    """
    Creates a markdown task file in the Needs_Action folder 
    when a new file is detected in the Inbox.
    """
    filename = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Define the new task filename: TASK_[original_filename]_[timestamp].md
    task_filename = f"TASK_{filename}_{timestamp}.md"
    task_path = os.path.join(ACTION_DIR, task_filename)
    
    # Content for the task file
    content = f"""# 🆕 New File Detected
- **File Name:** {filename}
- **Date Detected:** {date_str}
- **Status:** pending
- **Suggested Action:** review file
"""
    
    try:
        # Create the Needs_Action directory if it doesn't exist
        if not os.path.exists(ACTION_DIR):
            os.makedirs(ACTION_DIR)
            
        # Write the content to the new task file
        with open(task_path, "w") as f:
            f.write(content)
        
        print(f"✅ Created task: {task_filename}")
        
    except Exception as e:
        print(f"❌ Error creating task file: {e}")

# --- EVENT HANDLER ---
class InboxHandler(FileSystemEventHandler):
    """
    Inherits from FileSystemEventHandler to define what happens 
    when file system events occur.
    """
    def on_created(self, event):
        # We only care about files, not directories
        if not event.is_directory:
            print(f"📂 New file detected in Inbox: {event.src_path}")
            create_task_file(event.src_path)

# --- MAIN LOOP ---
if __name__ == "__main__":
    # Ensure the Inbox exists before watching it
    if not os.path.exists(WATCH_DIR):
        print(f"⚠️ Folder '{WATCH_DIR}' not found. Creating it...")
        os.makedirs(WATCH_DIR)

    # Initialize the event handler
    event_handler = InboxHandler()
    
    # Initialize the observer
    observer = Observer()
    
    # Schedule the observer to watch the WATCH_DIR folder
    # recursive=False means it won't watch subfolders inside Inbox
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    
    print(f"🚀 Qurrat-AI File Watcher started! Monitoring: ./{WATCH_DIR}/")
    print("Press Ctrl+C to stop.")
    
    # Start the observer
    observer.start()
    
    try:
        # Keep the script running continuously
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Gracefully stop if the user presses Ctrl+C
        observer.stop()
        print("\n👋 File Watcher stopped.")
    
    observer.join()
