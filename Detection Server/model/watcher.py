import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Directory to watch
WATCH_FOLDER = "captured_data"

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"New file detected: {file_path}")
        
        # Run the prediction model script with the new file
        subprocess.run(["python3", "network_model.py", file_path])

if __name__ == "__main__":
    observer = Observer()
    event_handler = FileHandler()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    print(f"Watching folder: {WATCH_FOLDER} for new files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

