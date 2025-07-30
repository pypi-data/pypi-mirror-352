from fastapi import APIRouter, Depends
from deskset.router.unify import DesksetReqNumberInt
from ._noteapi import noteapi

router_stats = APIRouter(prefix='/stats')

@router_stats.get('/note-number')
async def note_number():
    return (await noteapi.get(f'/stats/note-number')).json()

@router_stats.get('/heatmap/{num}')
async def heatmap(req: DesksetReqNumberInt = Depends()):
    weeknum = req.num  # 统计范围：前 weeknum 周 + 本周
    return (await noteapi.get(f'/stats/heatmap/{weeknum}')).json()

@router_stats.get('/use-days')
async def use_days():
    return (await noteapi.get(f'/stats/use-days')).json()
