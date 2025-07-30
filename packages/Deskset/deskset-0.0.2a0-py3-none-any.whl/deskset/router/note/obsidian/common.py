from fastapi import APIRouter, Query

from ._manager import manager
from ._noteapi import noteapi

router_common = APIRouter(prefix='/common')

@router_common.get('/current-note')
async def get_current_note():
    return (await noteapi.get('/obsidian/current-note')).text

# 最近打开的笔记
@router_common.get('/recent-notes')
async def get_recent_notes():
    workspace = (await noteapi.get('/obsidian/workspace')).json()
    recent_files = workspace.get('lastOpenFiles', []) if isinstance(workspace, dict) else []

    # lastOpenFiles 第一个不是现在打开的笔记，需要修正
    # 比如：按顺序打开笔记 1、2、3
      # recent_files = [1, 2]
      # current_file = 3
    current_file = (await noteapi.get('/obsidian/current-note')).text
    recent_files = [current_file] + [file for file in recent_files if file != current_file]

    from pathlib import Path
    return [
        { 'name': Path(file).stem, 'path': file }
        for file in recent_files
        if isinstance(file, str) and file.endswith('.md')
    ]

# 在 Obsidian 中打开笔记，笔记路径 path 以仓库为根目录
@router_common.get('/open')
async def open(path: str = Query(None)):
    await noteapi.open(path)
