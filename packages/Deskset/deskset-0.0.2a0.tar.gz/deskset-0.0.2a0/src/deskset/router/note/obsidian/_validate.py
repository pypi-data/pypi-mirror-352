from __future__ import annotations

from pydantic import BaseModel


# ==== NoteAPI data.json 设置 ====
class Setting(BaseModel):
    host: str
    port: int
    username: str
    password: str

    profile: Profile

# 个性资料
class Profile(BaseModel):
    avatar: str
    name: str
    bio: str
