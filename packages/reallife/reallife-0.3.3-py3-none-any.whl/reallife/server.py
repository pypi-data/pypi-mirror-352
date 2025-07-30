from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

from .cli import receive_task, complete_task, list_all_tasks
from .workday_facade import WorkdayFacade

workday_facade = WorkdayFacade()

app = FastAPI()

def task_daily_midnight():
    """
    每天凌晨 0:00 执行的任务
    """
    print(f"任务：每天凌晨 0:00 执行。当前时间：{time.ctime()}")
    workday_facade.clear()

def task_weekday_3am():
    """
    工作日 3:00 执行的任务
    """
    print(f"任务：工作日 3:00 执行。当前时间：{time.ctime()}")
    workday_facade._morning_tasks()

def task_weekday_850am():
    """
    工作日 8:50 执行的任务
    """
    print(f"任务：工作日 8:50 执行。当前时间：{time.ctime()}")
    workday_facade._start_work_tasks()

# def task_weekday_10am():
#     """
#     工作日 10:00 执行的任务
#     """
#     workday_facade.add_person_tasks()

def task_weekday_6pm():
    """
    工作日 18:00 执行的任务
    """
    print(f"任务：工作日 18:00 执行。当前时间：{time.ctime()}")
    workday_facade._finish_work_tasks()

def task_weekday_7pm():
    """
    工作日 19:00 执行的任务
    """
    print(f"任务：工作日 19:00 执行。当前时间：{time.ctime()}")
    workday_facade._evening_tasks()

def task_weekend_5am():
    """
    休息日 5:00 执行的任务
    """
    print(f"任务：休息日 5:00 执行。当前时间：{time.ctime()}")
    workday_facade._rest()

scheduler = BackgroundScheduler()

# 每天的凌晨 0:00
scheduler.add_job(task_daily_midnight, CronTrigger(hour=0, minute=0))

# 工作日 (周一到周五) 的 3:00
scheduler.add_job(task_weekday_3am, CronTrigger(hour=3, minute=0, day_of_week='mon-fri'))

# 工作日 (周一到周五) 的 8:50
scheduler.add_job(task_weekday_850am, CronTrigger(hour=8, minute=50, day_of_week='mon-fri'))

# 工作日 (周一到周五) 的 10:00
# scheduler.add_job(task_weekday_10am, CronTrigger(hour=10, minute=0, day_of_week='mon-fri'))

# 工作日 (周一到周五) 的 18:00
scheduler.add_job(task_weekday_6pm, CronTrigger(hour=18, minute=0, day_of_week='mon-fri'))

# 工作日 (周一到周五) 的 19:00
scheduler.add_job(task_weekday_7pm, CronTrigger(hour=19, minute=0, day_of_week='mon-fri'))

# 休息日 (周六和周日) 的 5:00
scheduler.add_job(task_weekend_5am, CronTrigger(hour=5, minute=0, day_of_week='sat,sun'))


@app.on_event("startup")
async def startup_event():
    print("应用启动中...")
    scheduler.start()
    print("APScheduler 启动")

@app.on_event("shutdown")
def shutdown_event():
    print("应用关闭中...")
    scheduler.shutdown()
    print("APScheduler 关闭")

def adapter(text):
    import re
    # 使用正则表达式匹配 "当前任务：" 后面的内容，直到第一个空格或括号
    regex = r"当前任务：(.*?)(?:\s|\()"
    regex = r"当前任务：(.*?)(?:\n|$)"
    match = re.search(regex, text)

    if match:
        task_name = match.group(1)
        return task_name
    else:
        print(f'提取失败: -> {text}')
        return text

@app.get("/receive")
async def receive():
    result = receive_task()
    return {"message": adapter(result)}


@app.get("/complete")
async def complete():
    result = complete_task()
    return {"message": adapter(result)}



from pydantic import BaseModel
from typing import List

class TaskListRequest(BaseModel):
    tasks: List


@app.post("/update_tasks")
async def update_tasks(task_request:TaskListRequest):
    print(task_request.tasks,'tasks')
    result = workday_facade.add_person_tasks(task_request.tasks)
    return {"message": result}


@app.get("/list_tasks")
async def list_tasks():
    result = list_all_tasks()
    return {"message": result}


@app.get("/morning")
async def morning():
    result = workday_facade._morning_tasks()
    print(result)
    return {"message": "FastAPI and APScheduler configured."}

@app.get("/clear")
async def clear():
    workday_facade.clear()
    return {"message": "FastAPI and APScheduler configured."}


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
        default=8020,
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
