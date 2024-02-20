import argparse
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler


class ChangeHandler(PatternMatchingEventHandler):
    patterns = ["*.py"]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.process = self.start_process()
        super().__init__()

    def on_any_event(self, event: FileSystemEvent):
        if self.process and self.process.poll() is None:
            self.process.terminate()  # Attempt to terminate the previous process
            print(f"Terminating previous instance of {self.file_path}")
        print(
            f"Change detected in {event.src_path}, restarting {self.file_path}")
        # Use Popen to non-blockingly start the process
        self.process = self.start_process()

    def start_process(self):
        return subprocess.Popen(["python", self.file_path])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dev Watcher")
    parser.add_argument("--file-path", type=str,
                        required=True, help="File to reload on change")
    parser.add_argument("--watch-path", type=str, default=".",
                        help="Path to watch for changes")

    args = parser.parse_args()

    print(f"Watching {args.watch_path} for changes to {args.file_path}")

    event_handler = ChangeHandler(args.file_path)
    observer = Observer()
    observer.schedule(event_handler, path=args.watch_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            # Ensure the subprocess is terminated on script exit
            event_handler.process.terminate()
        print("Watcher stopped.")

    observer.join()
