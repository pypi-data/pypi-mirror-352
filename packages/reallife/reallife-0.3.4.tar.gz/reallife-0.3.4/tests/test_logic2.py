# task_func__2.py
from abc import ABC, abstractmethod
# 策略接口
class TaskExecutionStrategy(ABC):
    @abstractmethod
    def execute(self, task_context):
        """执行任务的特定逻辑"""
        pass
# 具体策略：提示任务执行策略 (人工执行)
class PromptTaskExecutionStrategy(TaskExecutionStrategy):
    def execute(self, task_context):
        # 对于 Prompt 任务，execute 方法主要被 State 调用以获取提示
        # handle() 方法是 State 模式中获取提示的地方
        # print(f"Inside PromptTaskExecutionStrategy.execute for '{task_context.name}'. Called by State.")
        # 返回状态提供的提示
        return task_context._state.handle(task_context)
# 具体策略：自动任务执行策略 (电脑自动执行)
class AutomaticTaskExecutionStrategy(TaskExecutionStrategy):
    def execute(self, task_context):
        print(f"Inside AutomaticTaskExecutionStrategy.execute for '{task_context.name}'. Running automatic task...")
        try:
            # 这里模拟自动任务的执行逻辑
            # 实际应用中，这里会调用外部服务、执行脚本、处理数据等
            if task_context.script_code:
                # 模拟执行脚本
                exec(task_context.script_code)
                print(f"Automatic task '{task_context.name}' executed successfully.")
                # 模拟执行成功
                return {"status": "success", "message": f"自动任务 '{task_context.name}' 执行完毕。"}
            else:
                print(f"Automatic task '{task_context.name}' has no script code.")
                # 模拟执行成功 (没有代码也算执行成功)
                return {"status": "success", "message": f"自动任务 '{task_context.name}' 没有提供脚本代码，但标记为完成。"}
        except Exception as e:
            print(f"Automatic task '{task_context.name}' execution failed: {e}")
            # 模拟执行失败
            return {"status": "failure", "message": f"自动任务 '{task_context.name}' 执行失败：{e}"}

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
        # For Prompt tasks, this is the initial prompt.
        # For Automatic tasks, this might just indicate it's pending execution.
        if isinstance(task_context.execution_strategy, PromptTaskExecutionStrategy):
             return f"请开始任务：{task_context.name}"
        elif isinstance(task_context.execution_strategy, AutomaticTaskExecutionStrategy):
             return f"自动任务 '{task_context.name}' 待执行。"
        else:
             return f"任务 '{task_context.name}' 待办。"

    def complete(self, task_context):
        # print(f"Task '{task_context.name}' from '{self.get_status()}' is being completed...")

        # If it's a Prompt task, move to InProgress (requires human action)
        if isinstance(task_context.execution_strategy, PromptTaskExecutionStrategy):
            print(f"Task '{task_context.name}' (Prompt) entering '进行中' state.")
            task_context.set_state(InProgressState())
            return f"任务 '{task_context.name}' 状态更新为：进行中"

        # If it's an Automatic task, execute the strategy directly and transition based on result
        elif isinstance(task_context.execution_strategy, AutomaticTaskExecutionStrategy):
            print(f"Task '{task_context.name}' (Automatic) executing strategy...")
            execution_result = task_context.execution_strategy.execute(task_context)
            # print(f"Automatic Task Execution Result: {execution_result}")

            if execution_result.get("status") == "success":
                print(f"Task '{task_context.name}' (Automatic) executed successfully. Entering '完成' state.")
                task_context.set_state(CompletedState())
                return f"自动任务 '{task_context.name}' 执行成功并完成。{execution_result.get('message', '')}"
            else:
                print(f"Task '{task_context.name}' (Automatic) execution failed. Entering '失败' state.")
                task_context.set_state(FailedState())
                return f"自动任务 '{task_context.name}' 执行失败。{execution_result.get('message', '')}"
        else:
             # Fallback for unknown strategy types
             print(f"Task '{task_context.name}' with unknown strategy attempting completion from Todo.")
             return f"任务 '{task_context.name}' 无法从待办状态完成，未知执行策略。"


    def get_status(self):
        return "待办"
class InProgressState(TaskState):
    def handle(self, task_context):
        if isinstance(task_context.execution_strategy, PromptTaskExecutionStrategy):
             return f"任务 '{task_context.name}' 正在进行中。请确认是否已完成？"
        else: # Should not happen for Automatic tasks as they complete directly from Todo
             return f"任务 '{task_context.name}' 正在进行中 (非典型状态)。"

    def complete(self, task_context):
        # print(f"Task '{task_context.name}' from '{self.get_status()}' entering '完成' state")
        # Only Prompt tasks should reach InProgress state and be completed from here
        if isinstance(task_context.execution_strategy, PromptTaskExecutionStrategy):
             task_context.set_state(CompletedState())
             return f"任务 '{task_context.name}' 已标记为：完成"
        else:
             return f"任务 '{task_context.name}' ({type(task_context.execution_strategy).__name__}) 无法从进行中状态完成。"

    def get_status(self):
        return "进行中"
class CompletedState(TaskState):
    def handle(self, task_context):
        return f"任务 '{task_context.name}' 已完成。"
    def complete(self, task_context):
        return f"任务 '{task_context.name}' 已处于完成状态，无需重复操作。"
    def get_status(self):
        return "完成"
# 新增：失败状态
class FailedState(TaskState):
    def handle(self, task_context):
        return f"任务 '{task_context.name}' 执行失败。请检查。"
    def complete(self, task_context):
        # 可以选择在这里实现重试逻辑，或者标记为“已解决”等
        # 为简单起见，这里不允许从失败状态直接完成，需要其他操作（如重置）
        return f"任务 '{task_context.name}' 处于失败状态，无法直接标记为完成。需要重置或检查原因。"
    def get_status(self):
        return "失败"
# 任务类
class Task:
    def __init__(self, name: str, execution_strategy: TaskExecutionStrategy, script_code: str = None):
        self.name = name
        self._state = TodoState() # Initial state
        self.execution_strategy = execution_strategy
        self.script_code = script_code # Save script code
    def set_state(self, state: TaskState):
        """设置任务的当前状态"""
        # print(f"Task '{self.name}' transitioning from {self._state.get_status()} to {state.get_status()}")
        self._state = state
    def request(self):
        """获取任务状态和提示 - Calls state's handle method"""
        # Strategy's execute method for Prompt tasks is called by handle here.
        # Strategy's execute method for Automatic tasks is called by complete in TodoState.
        return self._state.handle(self)
    def complete_task(self):
        """尝试完成任务 - Calls state's complete method"""
        # State's complete method handles state transitions and triggers Automatic task execution if needed.
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
        print("任务管理器已清空。")

    def add_task(self, task_name: str, task_type='prompt', script_code: str = None):
        """动态添加任务"""
        if task_name in self._tasks:
            return f"任务 '{task_name}' 已存在。"
        if task_type == 'prompt':
            strategy = PromptTaskExecutionStrategy()
        elif task_type == 'automatic': # Changed from 'script'/'person' to a unified 'automatic'
            strategy = AutomaticTaskExecutionStrategy()
        else:
            strategy = PromptTaskExecutionStrategy() # Default
        new_task = Task(name=task_name, execution_strategy=strategy, script_code=script_code)
        self._tasks_order.append(task_name) # Add to ordered list
        self._tasks[task_name] = new_task   # Add to dictionary
        return f"任务 '{task_name}' ({task_type}) 已添加。"
    def get_task(self, task_name: str) -> Task | None:
        """获取指定名称的任务"""
        return self._tasks.get(task_name)
    def get_current_sequential_task(self) -> Task | None:
        """获取当前按顺序应执行的任务 (第一个未完成/失败的任务)"""
        # Consider FailedState as needing attention, so it's also a potential "current" task
        for task_name in self._tasks_order:
            task = self._tasks.get(task_name)
            # Return the first task that is not Completed
            if task and not isinstance(task._state, CompletedState):
                return task
        return None # All tasks completed
    def complete_current_task(self):
        """完成当前按顺序应执行的任务"""
        current_task = self.get_current_sequential_task()
        if current_task:
            # Calls the task's complete_task method, which calls the state's complete method
            # If the state is TodoState and strategy is Automatic, the script executes here.
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
# reallife__2.py (Updated Facade and CLI interaction)
# from .task_func__2 import TaskManager, PromptTaskExecutionStrategy, AutomaticTaskExecutionStrategy, TodoState, InProgressState, CompletedState, FailedState
# Global TaskManager instance
task_manager = TaskManager()
# Workday Facade
class WorkdayFacade:
    """工作日外观类，为日常任务处理提供统一接口"""
    def __init__(self):
        pass # Mock objects no longer needed with simplified strategies
    def clear(self):
        task_manager.clear()
    def _morning_tasks(self) -> str:
        """清晨任务"""
        task_manager.add_task("记录灵感", task_type="prompt")
        task_manager.add_task("记录体重", task_type="prompt")
        task_manager.add_task("跑步", task_type="prompt")
        task_manager.add_task("记录吃了什么", task_type="prompt")
        task_manager.add_task("洗漱护肤", task_type="prompt")
        task_manager.add_task("收拾家与锻炼", task_type="prompt")
        return "清晨任务已添加"
    def _start_work_tasks(self) -> str:
        """开工任务"""
        task_manager.add_task("上班打卡", task_type="prompt")
        # These are now unified 'automatic' tasks with potential script_code
        task_manager.add_task("同步体重",task_type = "automatic",script_code = 'print("Executing Sync Weight Script")') # Added dummy script
        task_manager.add_task("汇总到预备池", task_type="automatic", script_code='print("Executing Aggregate Script")') # Added dummy script
        task_manager.add_task("同步到就绪池", task_type="automatic", script_code='print("Executing Sync Ready Script")') # Added dummy script
        task_manager.add_task("调整优先级", task_type="prompt") # This remains a prompt task
        task_manager.add_task("同步到执行池", task_type="automatic", script_code='print("Executing Sync Execute Script")') # Added dummy script
        task_manager.add_task("同步到日历", task_type="automatic", script_code='print("Executing Sync Calendar Script")') # Added dummy script
        task_manager.add_task("同步到备忘录", task_type="automatic", script_code='print("Executing Sync Memo Script")') # Added dummy script
        task_manager.add_task("倒水", task_type="prompt")
        task_manager.add_task("写下灵感", task_type="prompt")
        task_manager.add_task("跟进阻塞池", task_type="prompt")
        return "开工任务已添加"

    def _finish_work_tasks(self) -> str:
        """收工任务"""
        task_manager.add_task("同步体重 (收工)", task_type="automatic", script_code='print("Executing Sync Weight (End of Day) Script")') # Added dummy script
        task_manager.add_task("同步到备忘录 (收工)", task_type="automatic", script_code='print("Executing Sync Memo (End of Day) Script")') # Added dummy script
        task_manager.add_task("检查和收集咨询", task_type="prompt")
        task_manager.add_task("检查是否仍在禅模式", task_type="prompt")
        task_manager.add_task("检测git提交", task_type="prompt")
        task_manager.add_task("下班打卡", task_type="prompt")
        task_manager.add_task("倒水 (收工)", task_type="prompt")
        return "收工任务已添加"
    def _evening_tasks(self) -> str:
        """晚间休息任务"""
        task_manager.add_task("整理家里和猫猫", task_type="prompt")
        task_manager.add_task("晚上洗漱,刷牙,护肤", task_type="prompt")
        task_manager.add_task("锻炼", task_type="prompt")
        task_manager.add_task("睡觉", task_type="prompt")
        return "晚间任务已添加"

    def _rest(self) -> str:
        """周末休息任务"""
        task_manager.add_task("周末", task_type="prompt")
        task_manager.add_task("查看备忘录", task_type="prompt")
        task_manager.add_task("锻炼", task_type="prompt")
        task_manager.add_task("玩游戏", task_type="prompt")
        return "周末任务已添加"

    def add_person_tasks(self) -> str:
        """添加一些人工任务示例"""
        lists = ['任务1 (人工)','任务2 (人工)','任务3 (人工)','任务4 (人工)']
        for i in lists:
            task_manager.add_task(i,task_type='prompt') # Ensure they are 'prompt'
        return "人工任务示例已添加"

    def get_current_task_info(self):
         """
         获取当前任务的名称、状态和提示。
         此方法调用 task.request()，对于 Prompt 任务会获取提示；对于 Automatic 待办任务，提示其待执行。
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
        如果当前任务是待办的 Prompt 任务，状态变为进行中。
        如果当前任务是待办的 Automatic 任务，执行策略并根据结果变为完成或失败。
        如果当前任务是进行中的 Prompt 任务，状态变为完成。
        完成任务后，获取下一个任务信息并返回。
        """
        # print("尝试完成当前任务...")
        complete_message = task_manager.complete_current_task()
        # print(f"完成结果: {complete_message}")
        # 获取下一个任务信息（或更新后的当前任务信息）
        next_task_info = self.get_current_task_info() # Call receive via facade
        return f"{complete_message}\n---\n{next_task_info}" # Return both messages

    def get_all_tasks_status(self):
         """获取所有任务的列表和状态"""
         return task_manager.get_task_list()
# main__2.py (Updated CLI for new Facade methods)
import sys
# 导入 WorkdayFacade 和 TaskManager，以及 CLI 函数
# from reallife.realLife__2 import WorkdayFacade, receive, complete, task_manager, list_tasks # Adjust import path

# 创建 WorkdayFacade 实例
workday_facade = WorkdayFacade()

def receive_task():
    """获取当前任务信息、状态和提示。不触发脚本执行。"""
    print("\n执行动作 1: receive (获取当前任务信息和提示)")
    # receive 函数只获取信息和提示，不触发脚本执行 (Automatic 脚本在 complete Todo 时执行)
    print(workday_facade.get_current_task_info())

def complete_task():
    """
    完成当前任务。
    如果当前任务是待办脚本任务，将触发脚本执行并根据结果更新状态。
    完成任务后，获取下一个任务信息并返回。
    """
    print("\n执行动作 2: complete (完成当前任务)")
    # complete 函数会完成当前任务，如果当前是待办 Automatic 任务，会触发脚本执行
    # 完成后，会显示下一个任务的信息
    print(workday_facade.complete_current_task())
    # list_tasks() # Optional: display updated list after each completion

def list_all_tasks():
     """列出所有任务及其状态"""
     print("\n--- 所有任务状态 ---")
     tasks_list = workday_facade.get_all_tasks_status()
     if not tasks_list:
         print("当前没有任务。")
         return
     for name, status in tasks_list:
         print(f"- {name}: {status}")
     print("---------------------")

def show_help():
    print("\n可用动作：")
    print("  1: 获取当前任务信息和提示 (receive)")
    print("  2: 完成当前任务 (complete)")
    print("  3: 列出所有任务状态 (list)")
    print("  41: 添加清晨任务")
    print("  42: 添加开工任务 (包含自动任务)")
    print("  43: 添加人工任务示例")
    print("  44: 添加收工任务")
    print("  45: 添加晚间任务")
    print("  51: 添加周末休息任务")
    print("  0: 清空所有任务")
    print("  help: 显示帮助信息")
    print("  quit/exit: 退出程序")

def main():
    print("欢迎使用任务管理 CLI 工具！")
    show_help()
    while True:
        print('\n-----------------------------')
        command = input("请输入动作名称 (或 'help', 'quit'): ").strip().lower()
        if command == '1':
            receive_task()
        elif command == '2':
            complete_task()
        elif command == '3':
            list_all_tasks()
        elif command == '41':
            print(workday_facade._morning_tasks())
        elif command == '42':
            print(workday_facade._start_work_tasks())
        elif command == '43':
            print(workday_facade.add_person_tasks())
        elif command == '44':
            print(workday_facade._finish_work_tasks())
        elif command == '45':
            print(workday_facade._evening_tasks())
        elif command == '51':
             print(workday_facade._rest())
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