""" 系统工具箱 """

from datetime import datetime
import os
import requests
import importlib.resources
import yaml

def push_task(task:str, date:str):
    """推任务上去

    Args:
        task (str): 任务名
        date (str): 日期
    """
    requests.post(
        f"http://101.201.244.227:8000/action/{task}/{date}/execute",timeout=20)
    return 'success'

def reset_task(task:str,date:str)->str:
    """重置任务

    Args:
        task (str): 任务名
        date (str): 日期

    Returns:
        str: 系统消息
    """
    requests.post(
        f"http://101.201.244.227:8000/action/{task}/{date}/reset",timeout=20)
    return 'success'

def reset_tasks(date:str):
    """重置多任务

    Args:
        date (str): 日期
    """
    for task in ['同步进程池','同步预备池','同步就绪池','同步执行池',]:
        reset_task(task,date)



# Load configuration from YAML file
def load_config():
    with importlib.resources.open_text('reallife', 'config.yaml') as f:
        return yaml.safe_load(f)
    # with open('reallife/config.yaml', 'r', encoding='utf-8') as f:
    #     return yaml.safe_load(f)



def check_action_(func,debug=True):
    """一个执行动作的配装

    Args:
        func (object): 动作函数
        debug (bool, optional): 是否debug模式. Defaults to True.
    """
    result = func()
    if result and debug:
        print(func.__name__)


class Date:
    """日期, 来控制系统时间

    Returns:
        object: 单例模式
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,date:str = None,time:str = None):
        # 只有第一次初始化时设置值，后续的初始化调用不会更改实例的值
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.date = date or datetime.today().strftime("%Y-%m-%d")
            self.time = time or datetime.today().strftime("%H:%M:%S")

    def set_date(self,date):
        self.date = date

    def set_time(self,time):
        self.time = time



from .tools.status import status

def create_func(task:str,date:str)->object:
    """创建特定对象

    Args:
        task (str): 任务
        date (str, optional): 日期. Defaults to date.

    Returns:
        object: 状态函数
    """
    @status(task=task,date=date)
    def func_():
        return task
    return func_

def check_(func):
    """检查信息的封装

    Args:
        func (object): 信息方法

    Raises:
        TaskInfo: 遇到信息抛出消息等待被捕捉
    """
    result = func()
    if result:
        raise TaskInfo(result)
    
class TaskInfo(Exception):
    """任务的抛出机制

    Args:
        Exception (_type_): 抛出
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

