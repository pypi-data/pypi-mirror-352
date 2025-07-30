from abc import ABC, abstractmethod
# 策略接口
class TaskExecutionStrategy(ABC):
    @abstractmethod
    def execute(self, task_context):
        """执行任务的特定逻辑"""
        pass

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