import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import os
import signal

class ProcessManager:
    def __init__(self, name, command, working_dir):
        self.name = name
        self.command = command
        self.working_dir = working_dir
        self.process = None

    def start(self, output_callback, notify_callback):
        if self.process is None:
            def run():
                try:
                    self.process = subprocess.Popen(
                        self.command,
                        cwd=self.working_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        shell=True,
                        text=True,
                        preexec_fn=os.setsid  # Start in new process group
                    )
                    notify_callback(f"✅ {self.name} started successfully.\n")
                    for line in self.process.stdout:
                        output_callback(f"[{self.name}] {line}")
                except Exception as e:
                    notify_callback(f"❌ Failed to start {self.name}: {e}\n")
                finally:
                    self.process = None
            threading.Thread(target=run, daemon=True).start()
        else:
            notify_callback(f"⚠️ {self.name} is already running.\n")

    def stop(self, notify_callback):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                notify_callback(f"🛑 {self.name} stopped successfully.\n")
            except Exception as e:
                notify_callback(f"❌ Failed to stop {self.name}: {e}\n")
            finally:
                self.process = None
        else:
            notify_callback(f"⚠️ {self.name} is not running.\n")

class SentryIoTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SentryIoT Control Panel")
        self.root.geometry("800x600")

        self.text_area = ScrolledText(root, height=30, width=100, bg="black", fg="lime", font=("Courier", 10))
        self.text_area.pack(pady=10)

        self.model_proc = ProcessManager("Model", "python3 watcher.py", os.path.expanduser("~/Desktop/Detection Server"))
        self.backend_proc = ProcessManager("Backend", "python3 dashboard_api.py", os.path.expanduser("~/Desktop/Detection Server/backend"))
        self.frontend_proc = ProcessManager("Frontend", "npm start", os.path.expanduser("~/Desktop/Detection Server/frontend"))

        self.add_controls()

    def add_controls(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Button(frame, text="Start Model", width=15, command=lambda: self.model_proc.start(self.log, self.log)).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Stop Model", width=15, command=lambda: self.model_proc.stop(self.log)).grid(row=0, column=1, padx=5)

        tk.Button(frame, text="Start Backend", width=15, command=lambda: self.backend_proc.start(self.log, self.log)).grid(row=1, column=0, padx=5)
        tk.Button(frame, text="Stop Backend", width=15, command=lambda: self.backend_proc.stop(self.log)).grid(row=1, column=1, padx=5)

        tk.Button(frame, text="Start Frontend", width=15, command=lambda: self.frontend_proc.start(self.log, self.log)).grid(row=2, column=0, padx=5)
        tk.Button(frame, text="Stop Frontend", width=15, command=lambda: self.frontend_proc.stop(self.log)).grid(row=2, column=1, padx=5)

        tk.Button(frame, text="Exit", width=32, command=self.root.quit).grid(row=3, column=0, columnspan=2, pady=10)

    def log(self, message):
        self.text_area.insert(tk.END, message)
        self.text_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SentryIoTApp(root)
    root.mainloop()

