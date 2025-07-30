"""
提供对外的方法 提供一些带状态的消息 - 使用外观设计模式
"""
# from datetime import datetime
# from chinese_calendar import is_workday
# from reallife import KANBAN_PATH, WORK_CANVAS_PATH
# from reallife import Date, Setting

# # 子系统或辅助类
# from .actions.action import KanBanManager, APPIO
# from .utils import check_action_, push_task
# from .scripts.aifunc import judge_type
# from .scripts.applescript import ShortCut, Display
# from .tasks import clean_and_update, edit_coder, test_and_study
# from .tasks import design, meeting_and_talk
# from .tasks import task_failed, task_complete
# from .utils import check_, create_func, TaskInfo

from .task_func__1 import TaskManager

task_manager = TaskManager()


def get_current_task_for_user(manager: TaskManager):
    """
    获取当前应该向用户展示的任务，并触发其执行。
    """
    # 直接调用 TaskManager 中获取并执行第一个未完成任务的方法
    return manager.execute_first_unfinished_task()

def complete(task_name:str):
    """
    完成指定名称的任务。
    """
    # task_manager.complete_task(task_name) # 移除重复调用
    return task_manager.complete_task(task_name)

# 初始化子系统实例
# kbmanager = KanBanManager(kanban_path=KANBAN_PATH, pathlib=WORK_CANVAS_PATH)
# appio = APPIO() # 再做一个外观模式, 管理APP服务



class WorkdayFacade: # 外观类, 对接看板系统, 对接APP遥控器
    """
    工作日外观类，为日常任务处理提供统一接口
    """
    def __init__(self,kb_system,appio_system):
        self.kbmanager = kb_system
        self.appio = appio_system


    def _morning_tasks(self) -> str:
        """
        清晨任务
            记录灵感
            记录体重
            跑步
            记录吃了什么
            洗漱护肤
            收拾家与锻炼
        """
        task_manager.add_task("记录灵感")
        task_manager.add_task("记录体重")
        task_manager.add_task("跑步")
        task_manager.add_task("记录吃了什么")
        task_manager.add_task("洗漱护肤")
        task_manager.add_task("收拾家与锻炼")



    def _start_work_tasks(self) -> str:
        """
        开工任务
        """
        # try:
        #     check_(create_func(task='上班打卡', date=date))
        #     check_action_(self.kbmanager.sync_ready, debug)
        #     check_action_(self.kbmanager.sync_order, debug)
        #     check_action_(self.kbmanager.sync_weight, debug)
        #     check_(create_func(task='调整优先级', date=date))
        #     check_action_(self.kbmanager.sync_run, debug)
        #     check_action_(self.appio.sync_calulate, debug)
        #     check_action_(self.appio.sync_notes, debug)
        #     check_(create_func(task='倒水茶水', date=date))
        # except TaskInfo as e:
        #     return str(e)
        # return "开工任务完成"

        task_manager.add_task("上班打卡")
        task_manager.add_task("汇总到预备池",task_type = "script",script_code = None)
        task_manager.add_task("同步到就绪池",task_type = "script",script_code = None)
        task_manager.add_task("同步体重",task_type = "script",script_code = None)
        task_manager.add_task("调整优先级")
        task_manager.add_task("同步到执行池",task_type = "script",script_code = None)
        task_manager.add_task("同步到日历",task_type = "script",script_code = None)
        task_manager.add_task("同步到备忘录",task_type = "script",script_code = None)
        task_manager.add_task("倒水")

    def _daily_tasks(self, date: str) -> str:
        """
        日常任务列表处理
        """
        try:
            check_(create_func(task='写下灵感', date=date))
            check_(create_func(task='跟进阻塞池', date=date))
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
                meeting_and_talk(task) # 默认处理方式
            task_result = Display.display_dialog("判断", f"任务是否完成: ", buttons='"complete","blockage"', button_cancel=True)
            if task_result == 'complete':
                task_complete(task=task)
            elif task_result == 'blockage':
                # TODO 任务阻塞处理
                pass
            else:
                task_failed(task=task)
            # 移除完成的任务
            ShortCut.run_shortcut("移除完成的任务", task)
        except TaskInfo as e:
            return str(e)
        return "日常任务处理完成"

    def _finish_work_tasks(self, date: str, debug: bool) -> str:
        """
        收工任务
            ##
            检查和收集咨询
            检查是否仍在禅模式
            检测git提交
            下班打卡
            倒水茶水晚上

        """
        # try:
        #     # TODO 知识库整理
        #     check_action_(self.kbmanager.sync_weight, debug)
        #     check_action_(self.appio.sync_notes, debug)

        #     # 同步体重
        #     # 同步笔记本任务

        #     check_(create_func(task='检查和收集咨询', date=date))
        #     check_(create_func(task='检查是否仍在禅模式', date=date))
        #     check_(create_func(task='检测git提交', date=date))
        #     check_(create_func(task='下班打卡', date=date))
        #     check_(create_func(task='倒水茶水晚上', date=date))
        # except TaskInfo as e:
        #     return str(e)
        # return "收工任务完成"
        task_manager.add_task("同步体重",task_type = "script",script_code = None)
        task_manager.add_task("同步笔记",task_type = "script",script_code = None)
        task_manager.add_task("检查和收集咨询")
        task_manager.add_task("检查是否仍在禅模式")
        task_manager.add_task("检测git提交")
        task_manager.add_task("下班打卡")
        task_manager.add_task("倒水")


    def _evening_tasks(self, date: str) -> str:
        """
        晚间休息任务
            整理家里和猫猫
            晚上洗漱,刷牙,护肤
            锻炼
            睡觉
        """
        # try:
        #     check_(create_func(task='整理家里和猫猫', date=date))
        #     check_(create_func(task='晚上洗漱,刷牙,护肤', date=date))
        #     check_(create_func(task='锻炼', date=date))
        #     check_(create_func(task='睡觉', date=date))
        # except TaskInfo as e:
        #     return str(e)
        # return "晚间任务完成"
        task_manager.add_task("整理家里和猫猫")
        task_manager.add_task("晚上洗漱,刷牙,护肤")
        task_manager.add_task("锻炼")
        task_manager.add_task("睡觉")


    def handle_daily_schedule(self, server: bool = False) -> str:
        """
        根据当前时间处理日常任务（外观接口）
        Args:
            server (bool, optional): 是否服务器模式. Defaults to False.
        Returns:
            str: 任务执行结果消息
        """
        time_str = self.date_util.time
        date_str = self.date_util.date
        debug = self.setting_util.debug

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            if is_workday(date_obj):
                current_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")

                # 定义时间段
                time_8_50 = datetime.strptime(date_str + " 8:50:00", "%Y-%m-%d %H:%M:%S")
                time_10_00 = datetime.strptime(date_str + " 10:00:00", "%Y-%m-%d %H:%M:%S")
                time_18_00 = datetime.strptime(date_str + " 18:00:00", "%Y-%m-%d %H:%M:%S")
                time_19_00 = datetime.strptime(date_str + " 19:00:00", "%Y-%m-%d %H:%M:%S")
                time_23_00 = datetime.strptime(date_str + " 23:00:00", "%Y-%m-%d %H:%M:%S")

                if current_time < time_8_50:
                    return self._morning_tasks(date=date_str)
                elif time_8_50 < current_time <= time_10_00:
                    return self._start_work_tasks(date=date_str, debug=debug)
                elif time_10_00 <= current_time < time_18_00 and not server:
                    return self._daily_tasks(date=date_str)
                elif time_18_00 <= current_time < time_19_00:
                    return self._finish_work_tasks(date=date_str, debug=debug)
                elif time_19_00 <= current_time < time_23_00:
                    return self._evening_tasks(date=date_str)
                else:
                    return '当前时间段无特定任务'
            else:
                return self._rest_tasks(date=date_str)
        except Exception as e:
            return f"处理日常任务时发生错误: {e}"

    def complete_current_task(self) -> str:
        """
        完成当前任务
        """
        date = self.date_util.date
        # 这里需要获取当前正在进行的任务，原代码中的 receive 函数根据时间段返回任务信息，
        # 在外观模式下，我们可能需要一个更明确的方式来获取当前任务。
        # 为了保持与原代码逻辑一致，这里暂时模拟调用 daily_tasks 并尝试完成。
        # 实际应用中，这部分逻辑需要根据实际任务管理系统来调整。
        try:
            # 尝试获取当前正在处理的任务信息（这部分逻辑需要根据实际情况调整）
            # 假设 daily_tasks 已经确定了当前任务
            task_info = self._daily_tasks(date) # 这里只是模拟调用，实际需要获取任务对象
            if task_info == '无任务':
                return {"message": "当前无任务可完成"}

            # 如果能获取到具体的任务对象 task，则进行以下处理
            # result = push_task(task=task, date=date)
            # return {"message": result}
            return {"message": "完成任务逻辑待实现（需要获取具体任务对象）"} # 暂时返回占位消息

        except Exception as e:
             return f"完成任务时发生错误: {e}"


    def add_task_tip(self, task: str) -> str:
        """
        为任务添加提示
        """
        try:
            self.kbmanager.add_tips(task)
            return f"已为任务 '{task}' 添加提示"
        except Exception as e:
            return f"添加任务提示时发生错误: {e}"


def receive():   
    """完成当前任务
    """
    result = get_current_task_for_user(task_manager)
    return result




def complete(task_name:str):
    task_manager.complete_task(task_name)
    task_manager.complete_task(task_name)
