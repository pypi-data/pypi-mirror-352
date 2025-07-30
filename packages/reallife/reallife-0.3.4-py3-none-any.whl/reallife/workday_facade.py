# task_func__1.py

from .task_manager import TaskManager

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
        task_manager.add_task("预备池->就绪池",task_type = "automatic",script_code = None) # Added dummy script
        task_manager.add_task("调整优先级", task_type="prompt") # This remains a prompt task
        task_manager.add_task("->执行池", task_type="automatic", script_code=None) # Added dummy script
        task_manager.add_task("->日历->备忘录", task_type="automatic", script_code=None) # Added dummy script
        task_manager.add_task("倒水", task_type="prompt")
        task_manager.add_task("写下灵感", task_type="prompt")
        task_manager.add_task("跟进阻塞池", task_type="prompt")
        return "开工任务已添加"

    def _finish_work_tasks(self) -> str:
        """收工任务"""
        task_manager.add_task("同步体重 (收工)", task_type="automatic", script_code=None) # Added dummy script
        task_manager.add_task("同步到备忘录 (收工)", task_type="automatic", script_code=None) # Added dummy script
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

    def add_person_tasks(self,tasks) -> str: # TODO
        """添加一些人工任务示例"""
        lists = ['任务1 (人工)','任务2 (人工)','任务3 (人工)','任务4 (人工)']
        for i in tasks:
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













