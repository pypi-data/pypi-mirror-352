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
    
# 具体策略：提示任务执行策略 (人工执行)
class AutomaticTaskExecutionStrategy(TaskExecutionStrategy):
    def execute(self, task_context):
        # 对于 Prompt 任务，execute 方法主要被 State 调用以获取提示
        # handle() 方法是 State 模式中获取提示的地方
        # print(f"Inside PromptTaskExecutionStrategy.execute for '{task_context.name}'. Called by State.")
        # 返回状态提供的提示
        return task_context._state.handle(task_context + '!action')
    
