# task_func__1.py
from abc import ABC, abstractmethod

# 策略接口
class TaskExecutionStrategy(ABC):
    @abstractmethod
    def execute(self, task_context):
        """执行任务的特定逻辑"""
        pass

# 具体策略：提示任务执行策略
class PromptTaskExecutionStrategy(TaskExecutionStrategy):
    def execute(self, task_context):
        # Prompt 任务的执行就是返回状态提示，但这个方法现在主要由 State 调用
        # handle() 方法是 State 模式中获取提示的地方
        print(f"Inside PromptTaskExecutionStrategy.execute for '{task_context.name}'. This is called by State.")
        return task_context._state.handle(task_context)

# 具体策略：脚本任务执行策略
class ScriptTaskExecutionStrategy(TaskExecutionStrategy):
    def execute(self, task_context):
        print(f"Inside ScriptTaskExecutionStrategy.execute for '{task_context.name}'. Running script...")
        print('\n\n')
        print(task_context,'task_context') # <__main__.Task object at 0x102bdfd90> task_context
        print(task_context.name,'ccvvv')
        try:
            # 注意：安全问题！这里只是示例，实际应用中需要谨慎处理

            if task_context.name == '汇总到预备池':
                pass
            elif task_context.name == '同步到就绪池':
                pass
            elif task_context.name == '同步到执行池':
                pass
            elif task_context.name == '同步到日历':
                pass
            elif task_context.name == '同步到备忘录':
                pass
            elif task_context.name == '同步体重':
                pass


            if task_context.script_code:
                # Execute the script code
                exec(task_context.script_code)
                return f"脚本任务 '{task_context.name}' 执行完毕。"
            else:
                 return f"脚本任务 '{task_context.name}' 没有提供脚本代码。"
        except Exception as e:
            # The state transition on failure would need to be handled by the caller (e.g., TodoState.complete)
            # Or we could return a special error message and let the State decide how to handle it.
            # For simplicity now, just return the error message.
            return f"脚本任务 '{task_context.name}' 执行失败：{e}"



class PersonTaskExecutionStrategy(TaskExecutionStrategy):

    def execute(self, task_context):
        print(f"Inside PersonTaskExecutionStrategy.execute for '{task_context.name}'. Running script...")
        print('\n\n')
        print(task_context,'task_context') # <__main__.Task object at 0x102bdfd90> task_context
        print(task_context.name,'ccvvv')
        try:
            # 注意：安全问题！这里只是示例，实际应用中需要谨慎处理
            # 执行动作
            pass

            if task_context.script_code:
                # Execute the script code
                exec(task_context.script_code)
                return f"脚本任务 '{task_context.name}' 执行完毕。"
            else:
                 return f"脚本任务 '{task_context.name}' 没有提供脚本代码。"
        except Exception as e:
            # The state transition on failure would need to be handled by the caller (e.g., TodoState.complete)
            # Or we could return a special error message and let the State decide how to handle it.
            # For simplicity now, just return the error message.
            return f"脚本任务 '{task_context.name}' 执行失败：{e}"



##################
# 任务状态接口 # 状态模式
class TaskState(ABC):
    @abstractmethod
    def handle(self, task_context):
        """处理当前状态下的任务逻辑 - 获取提示信息"""
        pass

    @abstractmethod
    def complete(self, task_context):
        """尝试完成任务 - 推进状态"""
        pass

    @abstractmethod
    def get_status(self):
        """获取当前状态描述"""
        pass

# 具体状态类
class TodoState(TaskState):
    def handle(self, task_context):
        # handle for Todo state just returns the initial prompt
        return f"请开始任务：{task_context.name}"

    def complete(self, task_context):
        # print(f"Task '{task_context.name}' from '待办' entering '进行中' state")
        # BEFORE changing state, execute the strategy if it's a ScriptTask
        # This is the trigger point for script execution

        if isinstance(task_context.execution_strategy, ScriptTaskExecutionStrategy) or \
           isinstance(task_context.execution_strategy, PersonTaskExecutionStrategy):
            #  print(f"Task '{task_context.name}' is an executable task type (Script/Person). Executing strategy on starting...")
             # Execute the strategy
             execution_result = task_context.execution_strategy.execute(task_context)
            #  print(f"Strategy Execution Result: {execution_result}") # Print the result of the execution
             # Note: The task's state is set to InProgress regardless of execution success/failure here.
             # You might want to add a FailureState if execution fails significantly.

        # Now change the state to InProgress
        task_context.set_state(InProgressState())
        return f"任务 '{task_context.name}' 状态更新为：进行中"

    def get_status(self):
        return "待办"

class InProgressState(TaskState):
    def handle(self, task_context):
        return f"任务 '{task_context.name}' 正在进行中。请确认是否已完成？"

    def complete(self, task_context):
        # print(f"Task '{task_context.name}' from '进行中' entering '完成' state")
        task_context.set_state(CompletedState())
        return f"任务 '{task_context.name}' 已标记为：完成"

    def get_status(self):
        return "进行中"

class CompletedState(TaskState):
    def handle(self, task_context):
        return f"任务 '{task_context.name}' 已完成。"

    def complete(self, task_context):
        return f"任务 '{task_context.name}' 已处于完成状态，无需重复操作。"

    def get_status(self):
        return "完成"

# 任务类
class Task:
    def __init__(self, name: str, execution_strategy: TaskExecutionStrategy, script_code: str = None):
        self.name = name
        self._state = TodoState() # Initial state
        self.execution_strategy = execution_strategy
        self.script_code = script_code # Save script code

    def set_state(self, state: TaskState):
        """设置任务的当前状态"""
        self._state = state

    def request(self):
        """获取任务状态和提示 - Calls state's handle method"""
        # Strategy's execute method is NOT called directly here anymore.
        return self._state.handle(self)

    def complete_task(self):
        """尝试完成任务 - Calls state's complete method"""
        # State's complete method will handle state transitions and potentially trigger script execution (in TodoState)
        return self._state.complete(self)

    def get_status(self):
        """获取当前任务状态描述"""
        return self._state.get_status()

# 任务管理器类
class TaskManager:
    def __init__(self):
        self._tasks_order = [] # Ordered list of task names
        self._tasks = {} # Dictionary to store task objects

    def clear(self):
        self._tasks_order = []
        self._tasks = {}

    def add_task(self, task_name: str, task_type='prompt', script_code: str = None):
        """动态添加任务"""
        if task_name in self._tasks:
            return f"任务 '{task_name}' 已存在。"
        if task_type == 'prompt':
            strategy = PromptTaskExecutionStrategy()
        elif task_type == 'script':
            strategy = ScriptTaskExecutionStrategy()
        elif task_type == 'person':
            strategy = PersonTaskExecutionStrategy()  
        else:
            strategy = PromptTaskExecutionStrategy() # Default
        new_task = Task(name=task_name, execution_strategy=strategy, script_code=script_code)
        # print(strategy,'strategy')
        self._tasks_order.append(task_name) # Add to ordered list
        self._tasks[task_name] = new_task   # Add to dictionary
        return f"任务 '{task_name}' 已添加。"

    def get_task(self, task_name: str) -> Task | None:
        """获取指定名称的任务"""
        return self._tasks.get(task_name)

    def get_current_sequential_task(self) -> Task | None:
        """获取当前按顺序应执行的任务 (第一个未完成的任务)"""
        for task_name in self._tasks_order:
            task = self._tasks.get(task_name)
            # Return the first task that is not completed
            if task and not isinstance(task._state, CompletedState):
                return task
        return None # All tasks completed

    def complete_current_task(self):
        """完成当前按顺序应执行的任务"""
        current_task = self.get_current_sequential_task()
        if current_task:
            # Calls the task's complete_task method, which calls the state's complete method
            # If the state is TodoState and strategy is Script, the script executes here.
            return current_task.complete_task()
        else:
            return "没有当前需要完成的任务。"

    def get_task_status(self, task_name: str):
        """获取指定任务的状态"""
        task = self.get_task(task_name)
        if task:
            return f"任务 '{task_name}' 的状态是：{task.get_status()}"
        else:
            return f"任务 '{task_name}' 不存在。"

    def get_task_list(self):
        """获取所有任务及其状态"""
        return [(name, self.get_task_status(name)) for name in self._tasks_order]

# reallife__1.py
# from .task_func__1 import TaskManager, PromptTaskExecutionStrategy, ScriptTaskExecutionStrategy, TodoState, InProgressState, CompletedState

# Global TaskManager instance (for simplicity in this example)
task_manager = TaskManager()

# Workday Facade
class WorkdayFacade:
    """工作日外观类，为日常任务处理提供统一接口"""
    def __init__(self):
        pass

    def clear(self):
        task_manager.clear()

    def _morning_tasks(self) -> str:
        """清晨任务"""
        task_manager.add_task("记录灵感")
        task_manager.add_task("记录体重")
        task_manager.add_task("跑步")
        task_manager.add_task("记录吃了什么")
        task_manager.add_task("洗漱护肤")
        task_manager.add_task("收拾家与锻炼")
        return "清晨任务已添加"

    def _start_work_tasks(self) -> str:
        """开工任务"""
        task_manager.add_task("上班打卡", task_type="prompt")
        task_manager.add_task("同步体重",task_type = "script",script_code = None)
        task_manager.add_task("汇总到预备池", task_type="script", script_code=None)
        task_manager.add_task("同步到就绪池", task_type="script", script_code=None)
        task_manager.add_task("调整优先级", task_type="prompt")
        task_manager.add_task("同步到执行池", task_type="script", script_code=None)
        task_manager.add_task("同步到日历", task_type="script", script_code=None)
        task_manager.add_task("同步到备忘录", task_type="script", script_code=None)
        task_manager.add_task("倒水", task_type="prompt")
        task_manager.add_task("写下灵感", task_type="prompt")
        task_manager.add_task("跟进阻塞池", task_type="prompt")
        return "开工任务已添加"



    def _finish_work_tasks(self) -> str:
        """收工任务"""
        task_manager.add_task("同步体重 (收工)", task_type="script", script_code=None)
        task_manager.add_task("同步到备忘录", task_type="script", script_code=None)
        task_manager.add_task("检查和收集咨询", task_type="prompt")
        task_manager.add_task("检查是否仍在禅模式", task_type="prompt")
        task_manager.add_task("检测git提交", task_type="prompt")
        task_manager.add_task("下班打卡", task_type="prompt")
        task_manager.add_task("倒水", task_type="prompt")
        return "收工任务已添加"

    def _evening_tasks(self) -> str:
        """晚间休息任务"""
        task_manager.add_task("整理家里和猫猫", task_type="prompt")
        task_manager.add_task("晚上洗漱,刷牙,护肤", task_type="prompt")
        task_manager.add_task("锻炼", task_type="prompt")
        task_manager.add_task("睡觉", task_type="prompt")
        return "晚间任务已添加"
    
    def _rest(self) -> str:
        """晚间休息任务"""
        task_manager.add_task("周末", task_type="prompt")
        task_manager.add_task("查看备忘录", task_type="prompt")
        task_manager.add_task("锻炼", task_type="prompt")
        task_manager.add_task("玩游戏", task_type="prompt")
        return "晚间任务已添加"
    
    

    def get_current_task_info(self):
         """
         获取当前任务的名称、状态和提示。
         此方法不触发脚本执行。
         """
         current_task = task_manager.get_current_sequential_task()
         if current_task:
             # Call request() to get the handle message/prompt from the current state
             prompt = current_task.request()
             return f"当前任务：{current_task.name} ({current_task.get_status()})\n提示: {prompt}"
         else:
             return "所有任务已完成！"

    def complete_current_task(self) -> str:
        """
        完成当前按顺序应执行的任务。
        如果当前任务是待办的脚本任务，将在此处触发脚本执行。
        """
        return task_manager.complete_current_task()

    def get_all_tasks_status(self):
         """获取所有任务的列表和状态"""
         return task_manager.get_task_list()


# --- CLI Interface Functions ---
# These functions interact with the WorkdayFacade
def receive():
    """获取当前任务信息、状态和提示。不触发脚本执行。"""
    return workday_facade.get_current_task_info()

def complete():
    """
    完成当前任务。
    如果当前任务是待办脚本任务，将触发脚本执行。
    完成任务后，获取下一个任务信息并返回。
    """
    # print("尝试完成当前任务...")
    complete_message = workday_facade.complete_current_task()
    # print(f"完成结果: {complete_message}")

    # 获取下一个任务信息（或更新后的当前任务信息）
    next_task_info = receive() # Call receive to get info about the new current task (or the completed one)
    return next_task_info

def list_tasks():
     """列出所有任务及其状态"""
    #  print("--- 所有任务状态 ---")
     tasks_list = workday_facade.get_all_tasks_status()
     if not tasks_list:
        #  print("当前没有任务。")
         return
     for name, status in tasks_list:
         print(f"- {name}: {status}")
     print("---------------------")


# main.py
import sys
# 导入 WorkdayFacade 和 TaskManager，以及 CLI 函数
# from reallife.realLife__1 import WorkdayFacade, MockKBManager, MockAPPIO, receive, complete, task_manager, list_tasks

# 创建 WorkdayFacade 实例，传入模拟对象
workday_facade = WorkdayFacade()

# 在程序启动时添加任务 (强制添加开工任务用于演示)
# print("添加任务中...")
# print(workday_facade._start_work_tasks()) # 直接调用添加方法，忽略时间判断
# print("任务添加完成。")



# list_tasks() # 显示初始任务列表和状态


def receive_1():
    print("\n执行动作 1: receive (获取当前任务信息和提示)")
    # receive 函数只获取信息和提示，不触发脚本执行 (脚本在 complete Todo 时执行)
    print(receive())

def complete_1():
    print("\n执行动作 2: complete (完成当前任务)")
    # complete 函数会完成当前任务，如果当前是待办脚本任务，会触发脚本执行
    # 完成后，会显示下一个任务的信息
    print(complete())
    # list_tasks() # 显示更新后的任务列表和状态





def show_help():
    print("\n可用动作：")
    print("  1: 获取当前任务信息和提示 (不触发脚本执行)")
    print("  2: 完成当前任务 (待办脚本任务会在此处执行，然后显示下一个任务)")
    print("  3: 列出所有任务状态")
    print("  help: 显示帮助信息")
    print("  quit/exit: 退出程序")

def main():
    print("欢迎使用简单的 CLI 工具！")
    show_help()
    while True:
        print('\n-----------------------------')
        command = input("请输入动作名称 (或 'help', 'quit'): ").strip().lower()
        if command == '1':
            receive_1()
        elif command == '2':
            complete_1()
        elif command == '3':
            list_tasks()
        elif command == '3':
            list_tasks()
        elif command == '41':
            workday_facade._morning_tasks()
        elif command == '42':
            workday_facade._start_work_tasks()
        elif command == '43':
            lists = ['任务1','任务2','任务3','任务4']
            for i in lists:
                task_manager.add_task(i,task_type='person')
        elif command == '44':
            workday_facade._finish_work_tasks()
        elif command == '45':
            workday_facade._evening_tasks()

        elif command == '51':
            workday_facade._rest()

        elif command == '0':
            workday_facade.clear()

        elif command == 'help':
            show_help()
        elif command in ['quit', 'exit']:
            print("退出程序。")
            break
        else:
            print(f"未知命令: {command}")
            show_help()

if __name__ == "__main__":
    main()
