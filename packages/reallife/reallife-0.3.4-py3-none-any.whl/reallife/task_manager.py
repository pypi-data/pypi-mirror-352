
from .task_state import TaskState, TodoState, CompletedState
from .execution_strategy import AutomaticTaskExecutionStrategy, PromptTaskExecutionStrategy, TaskExecutionStrategy
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