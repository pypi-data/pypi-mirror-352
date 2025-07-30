from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Dict, Optional

app = FastAPI()

# 模拟数据库
weight_records: Dict[date, float] = {}
action_status: Dict[str, bool] = {}  # 用于存储动作状态

class WeightRecord(BaseModel):
    weight: float
    date: date

class Action(BaseModel):
    action_id: str

# 获取动作状态
@app.get("/action/{action_id}/{date}/status")
async def get_action_status(action_id: str,date: str):
    """
    获取指定动作的状态
    """
    print(type(date))

    action_id += date
    return {"action_id": action_id, "status": "已执行" if action_status.get
            (action_id) else "未执行"}

# 执行动作并更新状态
@app.post("/action/{action_id}/{date}/execute")
async def execute_action(action_id: str,date: str):
    """
    执行指定动作并将状态改为已执行
    """
    action_id += date
    if action_id not in action_status:
        action_status[action_id] = False  # 初始化状态为未执行
    
    # 执行动作逻辑
    if action_id == "record_weight":
        # 示例：记录体重
        weight_records[date.today()] = 70.5  # 假设记录今天的体重为 70.5 kg
    elif action_id == "reset_weight":
        # 示例：重置体重记录
        weight_records.clear()
    elif action_id == "get_water":
        # 示例：记录接水时间
        print(f"接水时间：{date.today()}")
    elif action_id == "check_in":
        # 示例：记录打卡时间
        print(f"打卡时间：{date.today()}")
    
    action_status[action_id] = True  # 更新状态为已执行
    return {"action_id": action_id, "status": "已执行"}

# 重置动作状态
@app.post("/action/{action_id}/{date}/reset")
async def reset_action(action_id: str,date: str):
    """
    将指定动作的状态重置为未执行
    """
    action_id += date
    if action_id not in action_status:
        raise HTTPException(status_code=404, detail=f"动作 {action_id} 不存在")
    
    action_status[action_id] = False  # 重置状态为未执行
    return {"action_id": action_id, "status": "未执行"}





# 记录体重
@app.post("/record/{weight}/{date}")
async def record_weight(weight: float, date: str):
    """
    记录体重
    """
    weight_records[date] = weight
    return {"message": f"体重记录成功：{date} - {weight} kg"}

# 获取指定日期的体重
@app.get("/weight/{date}")
async def get_weight(date: str):
    """
    获取指定日期的体重
    """
    query_date = date
    if query_date not in weight_records:
        raise HTTPException(status_code=404, detail="未找到指定日期的体重记录")
    
    return {"date": query_date, "weight": weight_records[query_date]}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
