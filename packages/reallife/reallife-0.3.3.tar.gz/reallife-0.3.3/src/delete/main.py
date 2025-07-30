""" 提供对外的方法 提供一些带状态的消息 """

from datetime import datetime
from chinese_calendar import is_workday
from delete import KANBAN_PATH,WORK_CANVAS_PATH
from delete import Date, Setting



from .actions.action import KanBanManager,APPIO
from .utils import check_action_, push_task
from .scripts.aifunc import judge_type
from .scripts.applescript import ShortCut, Display

from .tasks import clean_and_update, edit_coder, test_and_study
from .tasks import design, meeting_and_talk
from .tasks import task_failed,task_complete
from .utils import check_,create_func, TaskInfo

kbmanager = KanBanManager(kanban_path=KANBAN_PATH,pathlib=WORK_CANVAS_PATH)
appio = APPIO()


def receive(server:bool = False)->str:
    """领取一个任务(普通模式)

    Returns:
        str: 任务信息
    """
    time = Date().time
    date = Date().date
    DEBUG = Setting().debug
    if is_workday(datetime.strptime(date, '%Y-%m-%d').date()):
        time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        # Create datetime objects once to avoid repetition
        time_8_50 = datetime.strptime(date + " 8:50:00", "%Y-%m-%d %H:%M:%S")
        time_10_00 = datetime.strptime(date + " 10:00:00", "%Y-%m-%d %H:%M:%S") 
        time_18_00 = datetime.strptime(date + " 18:00:00", "%Y-%m-%d %H:%M:%S")
        time_19_00 = datetime.strptime(date + " 19:00:00", "%Y-%m-%d %H:%M:%S")
        time_23_00 = datetime.strptime(date + " 23:00:00", "%Y-%m-%d %H:%M:%S")

        
        if time < time_8_50:
            return morning(date=date)

        elif time_8_50 < time <= time_10_00:
            return start_work(date=date,debug=DEBUG)

        elif time_10_00 <= time < time_18_00 and (server is False):
            return tasks(date=date)

        elif time_18_00 <= time < time_19_00:
            return finish_work(date=date)

        elif time_19_00 <= time < time_23_00:
            return evening(date=date)

        return 'success'
    else:
        return rest(date=date)


def morning(date:str)->str:
    """清晨动作

    Returns:
        str: 系统消息
    """
    try:
        check_(create_func(task='记录灵感',date=date))
        check_(create_func(task='记录体重',date=date))
        check_(create_func(task='跑步',date=date))
        check_(create_func(task='记录吃了什么',date=date))
        check_(create_func(task='洗漱护肤',date=date))
        check_(create_func(task='收拾家与锻炼',date=date))
    except TaskInfo as e:
        return e

    return {"message":"任务没了"}

def start_work(date:str,debug=True)->str:
    """开工

    Args:
        debug (bool, optional): 是否调试模式. Defaults to True.

    Returns:
        str: 系统消息
    """
    try:
        check_(create_func(task='上班打卡',date=date))
        check_action_(kbmanager.sync_ready,debug)
        check_action_(kbmanager.sync_order,debug)
        check_action_(kbmanager.sync_weight,debug)
        check_(create_func(task='调整优先级',date=date))
        check_action_(kbmanager.sync_run,debug)
        # check_action_(sync_news) # 对方改版了,等着用pypeteer去做吧
        check_action_(appio.sync_calulate,debug)
        check_action_(appio.sync_notes,debug)
        check_(create_func(task='倒水茶水',date=date))
        # bulid知识库
    except TaskInfo as e:
        return e

    return {"message":"任务没了"}

def tasks(date:str):
    """任务列表

    Returns:
        str: 系统消息
    """
    try:
        check_(create_func(task='写下灵感',date=date))
        check_(create_func(task='跟进阻塞池',date=date))
        task = ShortCut.run_shortcut("获取任务")
        if not task:
            return '无任务'
        task_type = judge_type(task)
        if task_type == "代码与练习":
            edit_coder(task)
        elif task_type == "实验与学习":
            test_and_study(task)
        elif task_type == "整理与优化":
            clean_and_update(task)
        elif task_type == "设计":
            design(task)
        elif task_type == "开会与对齐":
            meeting_and_talk(task)
        else:
            print('新的类别')
            # 开会与对齐
            meeting_and_talk(task)
        task_result = Display.display_dialog("判断",f"任务是否完成: ",buttons='"complete","blockage"',button_cancel = True)

        if task_result == 'complete':
            # 完成任务
            task_complete(task=task)
        
        elif task_result == 'blockage':
            # 任务阻塞
            #TODO
            pass

        else:
            # 完成未任务
            task_failed(task=task)

        # 移除完成的任务
        task = ShortCut.run_shortcut("移除完成的任务",task)

    except TaskInfo as e:
        return e

    return {"message":"任务结束"}

def finish_work(date:str,debug=True):
    """收工动作

    Returns:
        str: 系统信息
    """
    try:
        #TODO 知识库整理
        check_action_(kbmanager.sync_weight,debug)
        check_action_(appio.sync_notes,debug)
        check_(create_func(task='检查和收集咨询',date=date))
        check_(create_func(task='检查是否仍在禅模式',date=date))
        check_(create_func(task='检测git提交',date=date))
        check_(create_func(task='下班打卡',date=date))
        check_(create_func(task='倒水茶水晚上',date=date))
    except TaskInfo as e:
        return e
    return {"message":"任务没了"}

def evening(date:str)->str:
    """晚间休息的任务

    Returns:
        str: 系统消息
    """
    try:
        check_(create_func(task='整理家里和猫猫',date=date))
        check_(create_func(task='晚上洗漱,刷牙,护肤',date=date))
        check_(create_func(task='锻炼',date=date))
        check_(create_func(task='睡觉',date=date))
    except TaskInfo as e:
        return e

    return {"message":"任务没了"}

def rest(date:str)->str:
    try:
        #TODO 强化型健身  1周一次 在突破技能   5000米 + 负重 + 拳击
        check_(create_func(task='吃早饭',date=date))
        check_(create_func(task='洗漱',date=date))
        check_(create_func(task='锻炼',date=date))
        check_(create_func(task='睡觉',date=date))
    except TaskInfo as e:
        return e
    return {"message":"任务没了"}



def complete():
    """完成当前任务
    """
    date = Date().date
    task = receive()
    result = push_task(task=task,date=date)
    return {"message":result}


def add_tip(task:str):
    return kbmanager.add_tips(task)
