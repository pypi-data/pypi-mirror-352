import psutil
import time
import threading

class ManagedProcess:
    def __init__(self, process, start_time):
        self.process = process
        self.start_time = start_time
        self.pid = process.pid

    def terminate(self):
        self.process.terminate()

    def kill(self):
        self.process.kill()

    def is_running(self):
        return self.process.poll() is None

    def resource_usage(self):
        try:
            p = psutil.Process(self.pid)
            with p.oneshot():
                return {
                    "cpu_percent": p.cpu_percent(interval=0.1),
                    "memory_percent": p.memory_percent(),
                    "memory_info": p.memory_info()._asdict(),
                    "status": p.status(),
                    "threads": p.num_threads()
                }
        except Exception as e:
            return {"error": str(e)}

    def running_time(self):
        if self.is_running():
            return time.time() - self.start_time
        return None

class ProcessManager:
    def __init__(self):
        self._processes = {}

    def add(self, tag, managed_process):
        self._processes[tag] = managed_process

    def get(self, tag):
        return self._processes.get(tag)

    def terminate(self, tag):
        proc = self.get(tag)
        if proc:
            proc.terminate()
            return True
        return False

    def kill(self, tag):
        proc = self.get(tag)
        if proc:
            proc.kill()
            return True
        return False

    def all(self):
        return self._processes
