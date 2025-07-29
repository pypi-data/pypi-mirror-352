import time
from tasklauncher.core import TaskLauncher

def test_python_run():
    launcher = TaskLauncher()
    # 假设有个脚本 "example.py"，内容为 print("Hello, World!")
    result = launcher.run_python("tests/example.py")
    tag = result['tag']
    assert result['status'] == "started"
    info = launcher.task_status(tag)
    assert info["is_running"] is True
    # 等待完成
    out = launcher.wait_task(tag)
    assert "Hello, World!" in out["stdout"]

def test_stop_and_resource():
    launcher = TaskLauncher()
    result = launcher.run_command(["python", "-c", "import time; time.sleep(5)"])
    tag = result["tag"]
    time.sleep(1)
    status = launcher.task_status(tag)
    assert status["is_running"]
    res = status["resource"]
    assert "cpu_percent" in res
    stopped = launcher.stop_task(tag)
    assert stopped

# 可在 tests/ 目录下新建 example.py 以用于测试
# 内容如下：
# print("Hello, World!")
