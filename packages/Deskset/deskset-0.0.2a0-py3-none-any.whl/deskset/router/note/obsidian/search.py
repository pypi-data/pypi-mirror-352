from fastapi import APIRouter, Query
from ._noteapi import noteapi

router_search = APIRouter(prefix='/search')

cache_notes: list[str] = []
@router_search.get('/note')
async def find_note(query: str = Query(None)):
    global cache_notes
    # /note 传入 None，/note?query= 传入 ''。两者均代表结束查询
    if query == None or query == '':
        cache_notes = []
    else:
        if cache_notes == []:
            cache_notes = (await noteapi.get('/obsidian/all-notes')).json()
        return [note for note in cache_notes if query.lower() in note.lower()]
