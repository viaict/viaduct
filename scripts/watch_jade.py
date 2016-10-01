import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import platform


def compile_():
    if platform.system() == 'Windows':
        subprocess.call(('node node_modules/clientjade/bin/clientjade'
                         ' src/jade/ > src/js/global/jade.js'),
                        shell=True)
    else:
        subprocess.call(('./node_modules/clientjade/bin/clientjade'
                         ' src/jade/ > src/js/global/jade.js'),
                        shell=True)

# init jade files
compile_()


class EventHandler(FileSystemEventHandler):
    def process_x(self, event):
        if event.src_path[-5:] == '.jade':
            self.jade(event)

    def jade(self, event):
        print("modified: ", event.src_path)
        compile_()

    def on_created(self, event):
        self.process_x(event)

    def on_deleted(self, event):
        self.process_x(event)

    def on_modified(self, event):
        self.process_x(event)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()  # HAMMERTIME!
    observer.join()
