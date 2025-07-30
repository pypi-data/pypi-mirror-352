
from .abstra import TaskState
# from .execution_strategy import ScriptTaskExecutionStrategy, PersonTaskExecutionStrategy
from .execution_strategy import PromptTaskExecutionStrategy,AutomaticTaskExecutionStrategy
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