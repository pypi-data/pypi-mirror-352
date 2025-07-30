from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import re
import os
import click

EXCLUDED_FILES = {"ploomber-cloud.json", "README.md"}
EXCLUDED_PATTERN = re.compile(r"app-.*\.zip")


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        filename = event.src_path.split("/")[-1]

        if filename in EXCLUDED_FILES:
            return

        # Ignore dynamically generated zip files
        if EXCLUDED_PATTERN.match(filename):
            return

        click.echo(f"{filename} modified.")

        try:
            subprocess.run(["pc", "deploy"], check=True)
        except Exception:
            # pc deploy would raise the relevant error.
            pass


def start_watcher(path=None):
    """Start watching the given path for changes."""
    path = path or os.getcwd()

    click.echo(f"Watching for file changes in: {path}")
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer
