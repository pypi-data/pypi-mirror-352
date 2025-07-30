from fastapi import APIRouter, Depends
from deskset.router.unify import DesksetReqDateDay, DesksetReqDateMonth
from ._noteapi import noteapi

router_diary = APIRouter(prefix='/diary')

@router_diary.get('/today')
async def today():
    diary = (await noteapi.get(f'/diary/read-today')).json()
    return diary

@router_diary.get('/today-tasks')
async def today_tasks():
    diary = (await noteapi.get(f'/diary/read-today')).json()
    diary_tasks = (await noteapi.post(f'/tasks/get-all-tasks', data={'notepath': diary['notepath']})).json()
    return diary_tasks

# 读取某天日记（日期格式：YYYYMMDD）
@router_diary.get('/read-day/{day}')
async def read_day(date: DesksetReqDateDay = Depends()):
    diary = (await noteapi.get(f'/diary/read-day/{date.day}')).json()
    return diary

# 读取某月中的日记（日期格式：YYYYMM）
@router_diary.get('/read-month/{month}')
async def read_month(date: DesksetReqDateMonth = Depends()):
    diarys = (await noteapi.get(f'/diary/read-month/{date.month}')).json()
    return diarys
