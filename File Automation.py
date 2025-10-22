import sys
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import os
from os.path import splitext, exists, join

# --- Folder paths ---
source_dir = r"C:\Users\rryno\Downloads"
dest_dir_SM = r"C:\Users\rryno\Desktop\SoundandMusic"
dest_dir_video = r"C:\Users\rryno\Desktop\Video"
dest_dir_image = r"C:\Users\rryno\Desktop\Image"
dest_dir_doc = r"C:\Users\rryno\Desktop\Document"

# --- Ensure destination folders exist ---
for folder in [dest_dir_SM, dest_dir_video, dest_dir_image, dest_dir_doc]:
    os.makedirs(folder, exist_ok=True)


def Uniqueness(dest, name):
    """Return a unique filename if a duplicate exists in destination."""
    filename, extension = splitext(name)
    counter = 1
    new_name = name
    while exists(join(dest, new_name)):
        new_name = f"{filename}({counter}){extension}"
        counter += 1
    return new_name


def move(dest, entry, name):
    """Move the file safely to destination, renaming if needed."""
    if not entry.is_file():
        return  # skip folders and temp files

    new_name = Uniqueness(dest, name)
    src_path = entry.path
    dest_path = join(dest, new_name)

    try:
        shutil.move(src_path, dest_path)
        logging.info(f"Moved: {src_path} → {dest_path}")
    except Exception as e:
        logging.error(f"Error moving {src_path}: {e}")


class FileMovementHandler(LoggingEventHandler):
    """Event handler that moves files based on extension."""
    def on_modified(self, event):
        with os.scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name

                if name.lower().endswith(('.wav', '.mp3', '.flac')):
                    move(dest_dir_SM, entry, name)
                elif name.lower().endswith(('.pdf', '.docx', '.txt', '.xlsx')):
                    move(dest_dir_doc, entry, name)
                elif name.lower().endswith(('.mp4', '.mkv', '.avi')):
                    move(dest_dir_video, entry, name)
                elif name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    move(dest_dir_image, entry, name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    event_handler = FileMovementHandler()
    observer = Observer()
    observer.schedule(event_handler, source_dir, recursive=False)
    observer.start()

    logging.info(f"Watching for changes in: {source_dir}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
