import subprocess
import sys
import uuid
import time
import shlex
from .process_manager import ManagedProcess, ProcessManager
from .utils import get_system_info

class TaskLauncher:
    def __init__(self):
        self.manager = ProcessManager()
        self.system_info = get_system_info()

    def run_command(self, cmd, shell=False, cwd=None, env=None):
        """通用命令执行接口，返回tag、pid、启动信息"""
        tag = str(uuid.uuid4())
        try:
            if isinstance(cmd, str) and not shell:
                cmd = shlex.split(cmd)
            proc = subprocess.Popen(
                cmd, shell=shell, cwd=cwd, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            managed = ManagedProcess(proc, time.time())
            self.manager.add(tag, managed)
            return {
                "tag": tag,
                "pid": proc.pid,
                "status": "started",
                "system_info": self.system_info
            }
        except Exception as e:
            return {
                "tag": tag,
                "pid": None,
                "status": "error",
                "error": str(e)
            }

    def run_python(self, pyfile, *args, python_executable=sys.executable, cwd=None, env=None):
        """专门针对python脚本优化的入口"""
        cmd = [python_executable, pyfile] + list(map(str, args))
        return self.run_command(cmd, shell=False, cwd=cwd, env=env)

    def stop_task(self, tag, force=False):
        if force:
            return self.manager.kill(tag)
        else:
            return self.manager.terminate(tag)

    def task_status(self, tag):
        proc = self.manager.get(tag)
        if not proc:
            return {"error": "No such task"}
        return {
            "is_running": proc.is_running(),
            "resource": proc.resource_usage(),
            "running_time": proc.running_time()
        }

    def wait_task(self, tag, timeout=None):
        proc = self.manager.get(tag)
        if not proc:
            return {"error": "No such task"}
        try:
            outs, errs = proc.process.communicate(timeout=timeout)
            return {
                "returncode": proc.process.returncode,
                "stdout": outs.decode(errors='replace'),
                "stderr": errs.decode(errors='replace')
            }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout"}
