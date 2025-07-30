# my_cli.py
import sys

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "hello":
            print("Hello from CLI!")
            sys.exit(0)
        elif sys.argv[1] == "error":
            sys.stderr.write("This is an error.\n")
            sys.exit(1)
        else:
            print(f"Unknown command: {sys.argv[1]}")
            sys.exit(2)
    else:
        print("Please provide a command.")
        sys.exit(3)

if __name__ == "__main__":
    main()




# test_my_cli.py
import subprocess
import sys

def test_hello_command():
    # 执行 CLI 命令
    result = subprocess.run([sys.executable, "my_cli.py", "hello"], capture_output=True, text=True)

    # 断言标准输出
    assert "Hello from CLI!" in result.stdout
    # 断言标准错误是空的
    assert result.stderr == ""
    # 断言退出码
    assert result.returncode == 0

def test_error_command():
    result = subprocess.run([sys.executable, "my_cli.py", "error"], capture_output=True, text=True)

    # 断言标准错误
    assert "This is an error." in result.stderr
    # 断言标准输出是空的
    assert result.stdout == ""
    # 断言退出码
    assert result.returncode == 1

def test_unknown_command():
    result = subprocess.run([sys.executable, "my_cli.py", "unknown"], capture_output=True, text=True)

    # 断言标准输出
    assert "Unknown command: unknown" in result.stdout
    # 断言标准错误是空的
    assert result.stderr == ""
    # 断言退出码
    assert result.returncode == 2

def test_no_command():
    result = subprocess.run([sys.executable, "my_cli.py"], capture_output=True, text=True)

    # 断言标准输出
    assert "Please provide a command." in result.stdout
    # 断言标准错误是空的
    assert result.stderr == ""
    # 断言退出码
    assert result.returncode == 3




#################

import sys
import os
# 将项目根目录添加到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import re
import pytest

from delete.main import morning,push_task

from delete.main import rest,evening

from delete.main import start_work, finish_work

class Test_Morning():
    # @pytest.mark.skip(reason='通过')
    def test_morning(self):
        result = morning("2025-05-11")
        print(result)
        push_task(task=result,date = "2025-05-11")

    @pytest.mark.skip(reason='通过')
    def start_work(self):
        result = start_work("2025-05-11")
        print(result)
        push_task(task=result,date = "2025-05-11")

    @pytest.mark.skip(reason='通过')
    def finish_work(self):
        result = finish_work("2025-05-11")
        print(result)
        push_task(task=result,date = "2025-05-11")

    def test_evening(self):
        result = evening("2025-05-11")
        print(result)
        push_task(task=result,date = "2025-05-11")

    def test_rest(self):
        result = rest("2025-05-11")
        print(result)
        push_task(task=result,date = "2025-05-11")



