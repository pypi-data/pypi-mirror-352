""" 执行任务 """
from .actions.action import KanBanManager
from . import KANBAN_PATH, WORK_CANVAS_PATH
from .scripts.applescript import Display,ShortCut
import os


def git_commit_something(repo:str,commit:str):
    """提交git commit 

    Args:
        repo (str): 仓库
        commit (str): 提交信息
    """
    os.system(f"cd /Users/zhaoxuefeng/GitHub/{repo};git add .; \
              git commit -m '{commit}' --allow-empty")



def failed_safe():
    # 安全开启 放弃
    '''
    查询session状态
    如果 当前session 状态是 session
        放弃session
    否则
        pass
    结束
    '''
    ShortCut.run_shortcut(shortcut_name="安全停止")


def task_with_time(task_name:str,time:int=1):
    """计时任务

    Args:
        task_name (str): 任务名
        time (int, optional): 费用. Defaults to 1.
    """
    ShortCut.run_shortcut(shortcut_name="执行计时任务",params=f"{task_name}${time}")
    Display.display_dialog("计时结束", "需要结束计时任务吗?",buttons = '"结束"',button_cancel=False)



def edit_coder(task:str):
    """编写代码

    Args:
        task (str): 任务
    """

    # 是否创建项目
    create_proj = False

    Display.display_dialog("编写代码",f"是否创建新项目: {task}",buttons = '"开始`"',button_cancel=False)
    create_proj = Display.display_dialog("编写代码",f"是否创建新项目: ",buttons = '"创建"',button_cancel=True)
    if create_proj == 'create':
        Display.display_dialog("创建项目","1. pypi查重 \n  2. obsidian创建Reader | Docs \n \
                       3创建github仓库",buttons = '"确认"',button_cancel=False)
        Display.display_dialog("创建项目","初始化 uv init and 修改解释器 \
                       mkdocs new .  update  文档推送  创建文件夹,\
                       测试文件等  \
                       uv build publish  ",buttons = '"确认"', button_cancel=False)
    print(task,'task')
    # TODO
    lst = ['coderTools','grapher','kanban']

    all_options = ['coderTools','grapher','kanban','llmada','networkx','ob_ragtools','obsidian','promptlib',
                   'pypidoctor','readerLLamaIndex','reallife','tools','aiworker']
    choice = Display.multiple_selection_boxes(
        prompt_text="请选择作为工作区的仓库:",
        list_title="工作区",
        options=all_options,
        default_option="kanban"
    )
    if choice:
        select = choice
    else:
        select = None
        raise Exception('选择失效')
    #
    Display.display_dialog("编码与练习","基础逻辑",buttons = '"确认"',)
    task_with_time(task_name = task,time=40)
    Display.display_dialog("编码与练习","测试与测试用例",buttons = '"确认"',)
    task_with_time(task_name = task,time=30)
    Display.display_dialog("编码与练习","整理代码,注释,格式,文档与发布",buttons = '"确认"',)
    task_with_time(task_name = task,time=20)
    Display.display_dialog("编码与练习","环境与推送新版本",buttons = '"确认"',)
    task_with_time(task_name = task,time=10)
    # 仓库$编写目标
    git_commit_something(select,task)
    failed_safe()

def test_and_study(task:str):
    """实验与学习

    Args:
        task (str): 任务
    """
    # 实验与学习
    Display.display_dialog("实验与学习",f"请打开飞书会议, 标题为{task}",buttons = '"确认"',button_cancel=False)
    task_with_time(task_name = task,time=60)
    Display.display_dialog("实验与学习","自我审视+ 反思 + 分析笔记",buttons = '"确认"',button_cancel=False)
    failed_safe()

def clean_and_update(task:str):
    """整理与优化

    Args:
        task (str): 任务
    """
    Display.display_dialog("整理与优化",f"是否可以开始整理与优化: {task}",buttons = '"可以"',button_cancel=False)
    task_with_time(task_name = task,time=20)
    failed_safe()

def design(task:str):
    """设计

    Args:
        task (str): 任务名
    """
    Display.display_dialog("设计",f"准备开始设计: {task}",buttons = '"开始"',button_cancel=False)
    task_with_time(task_name = task,time=60)
    git_commit_something("obsidian",task)
    failed_safe()

def meeting_and_talk(task:str):
    """开会与对齐

    Args:
        task (str): 任务名
    """
    Display.display_dialog("开会与对齐",f"准备开会与对齐: {task}",buttons = '"开始"',button_cancel=False)
    task_with_time(task_name = task,time=60)
    failed_safe()



def task_complete(task):

    # 任务已完成
    # multi_line_input = "真实人生-将对应的执行池内容添加到完成池"

    """
     script/kanban_manager_2over_function.py
    任务$canvas_path
     script/kanban_manager_2over.py
    """
    project_paths = WORK_CANVAS_PATH
    # task = "真实人生-将对应的执行池内容添加到完成池"
    project = task.split('-',1)[0]
    now_project_path = None
    for project_path in project_paths:
        if project == project_path.split('/')[-2]:
            now_project_path = project_path

    kbm = KanBanManager(kanban_path=KANBAN_PATH,pathlib=WORK_CANVAS_PATH)
    print('now_project_path',now_project_path)
    if now_project_path:
        kbm.sync_run2over(task,canvas_path=now_project_path)
    try:
        canvas_path = now_project_path.replace('\n','')
        kbm.sync_run2over(task,canvas_path =canvas_path)
    except AttributeError as e:
        print('noe')
    return 'success'

##########


def task_failed(task):
    # 任务未完成
    """
     script/kanban_manager_runner2order.py
    """
    kbm = KanBanManager(kanban_path=KANBAN_PATH,pathlib=WORK_CANVAS_PATH)

    kbm.sync_run2order()
