import os
import sys
import time
import shutil
import threading


class StreamTee:
    def __init__(self, filename, mode="w"):
        self.lock = threading.Lock()
        self.file_path = filename
        self.file = open(filename, mode, encoding="utf-8")
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def reset(self, filename, mode="a"):
        with self.lock:
            self.file.close()
            shutil.copyfile(self.file_path, filename)
            os.remove(self.file_path)
            self.file = open(filename, mode, encoding="utf-8")
            self.file_path = filename

    def write(self, message):
        with self.lock:
            self.stdout.write(message)
            self.file.write(message)

    def flush(self):
        with self.lock:
            self.stdout.flush()
            self.file.flush()

    def isatty(self):
        return self.stdout.isatty()

    def close(self):
        with self.lock:
            self.file.close()
            sys.stdout = self.stdout
            sys.stderr = self.stderr


# 劫持 sys.stdout 和 sys.stderr
var_stream_tee = StreamTee(f"{time.time()}.tmp.log")
sys.stdout = var_stream_tee
sys.stderr = var_stream_tee
