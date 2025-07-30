from fastapi import FastAPI, Request
from pydantic import BaseModel # 导入 BaseModel

try:
    from delete.main import add_tip, complete, receive
    from delete.server_function import 
except ImportError as e:
    print(f"Error importing from reallife.core: {e}")
    print("Please ensure 'reallife' directory is in your Python path and contains 'core.py'.")
    # raise e

app = FastAPI()

# 定义一个用于接收 /tip/add 请求体的 Pydantic 模型
class TaskInput(BaseModel):
    task: str

# 定义一个根路径，方便测试服务是否启动
@app.get("/")
async def read_root():
    return {"message": "RealLife Core API is running"}

# 封装 add_tip 函数
# 现在接受一个 TaskInput 模型作为请求体
@app.post("/tip/add")
# 将参数类型改为 TaskInput 模型，并给一个默认值（表示它来自请求体）
async def api_add_tip(task_input: TaskInput): # 参数名可以随意，但类型是 TaskInput
    """
    调用 reallife.core.add_tip 函数，为任务添加提示。
    接收一个 JSON 对象，例如: {"task": "你的任务描述"}
    """
    # 从模型实例中获取 task 字符串
    result = add_tip(task_input.task)
    return {"result": result} # 可以根据 add_tip 的实际返回值调整结构

# 封装 complete 函数 (保持不变)
@app.post("/complete")
async def api_complete():
    """
    调用 reallife.core.complete 函数，完成任务。
    """
    result = complete()
    return {"result": result}

# 封装 receive 函数 (保持不变)
@app.get("/receive")
async def api_receive(request: Request):
    """
    调用 reallife.core.receive 函数，接收一些数据或信息。
    可以通过应用状态 (app.state) 获取启动时传入的参数。
    """
    # 从应用状态中获取 server 参数的值
    # 使用 .get() 方法可以在键不存在时返回 None，避免 KeyError
    # 或者提供一个默认值，例如 False
    is_server_status = request.app.state.is_server_status
    result = receive(server=is_server_status)
    return {"result": result}



if __name__ == "__main__":
    # 这是一个标准的 Python 入口点惯用法
    # 当脚本直接运行时 (__name__ == "__main__")，这里的代码会被执行
    # 当通过 python -m YourPackageName 执行 __main__.py 时，__name__ 也是 "__main__"
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?', # 端口是可选的
        default=8001,
        help='Specify alternate port [default: 8000]'
    )

    parser.add_argument(
        '--is-server',
        action='store_true', # 如果命令行中包含 --is-server，则将 args.is_server 设置为 True
        help='Set the server status for the receive function to True'
    )

    args = parser.parse_args()
    app.state.is_server_status = args.is_server

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
        reload=False  # 启用热重载
    )
