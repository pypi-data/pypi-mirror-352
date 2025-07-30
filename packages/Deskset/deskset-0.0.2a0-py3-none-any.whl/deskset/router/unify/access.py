# 检查参数
import sys

DEVELOP_ENV = False     # 开发环境
DISABLE_ACCESS = False  # （仅限开发环境）是否禁用认证，方便调试
ACCESS_TOKEN = None     # （不为空，见下）使用命令行传入的 token

for arg in sys.argv:
    if arg == '-dev':
        DEVELOP_ENV = True
        continue
    if arg == '-no-access':
        DISABLE_ACCESS = True
        continue
    if arg.startswith('-token='):
        token = arg.replace('-token=', '')
        if token != '':
            ACCESS_TOKEN = token
        continue


# access 权限
from deskset.core.config import config

if DISABLE_ACCESS:
    from deskset.core.log import logging
    logging.warning('=== Access is disabled ===')


class Access(object):
    def __init__(self) -> None:
        self._token: str = self._generate_token(config.username, config.password)

    def _generate_token(self, username: str, password: str) -> str:
        from datetime import datetime
        current: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        import os
        key: bytes = os.urandom(32)
        msg: bytes = (username + current + password).encode()

        import hmac
        import hashlib
        token: str = hmac.new(key, msg, hashlib.sha256).hexdigest()

        return token

    @property
    def token(self) -> str:
        # return self._token  # - [ ] 临时：不返回正确 token
        return 'use -token= instead'

    def set_token(self, token: str) -> None:
        self._token = token

    def get_token(self) -> str:
        return self._token

access = Access()

if ACCESS_TOKEN is not None:
    access.set_token(ACCESS_TOKEN)


# oauth2_scheme 获取 token => check_token 验证 token
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v0/access/login')  # tokenUrl 写全 URL

def check_token(token: str = Depends(oauth2_scheme)) -> bool:  # Depends(oauth2_scheme) 拿取 request.token
    if token != access.token:
        raise HTTPException(status_code=400, detail='无效密钥')
    return True

if DISABLE_ACCESS:
    if not DEVELOP_ENV:  # 只有开发环境，才能禁用认证，否则直接退出（DISABLE_ACCESS = True 被意外打包）
        from deskset.core.log import logging
        logging.critical('DISABLE_ACCESS is True on Product Environment')
        raise RuntimeError('DISABLE_ACCESS is True on Product Environment')
    def check_token() -> None:  # 重新定义 check_token（注：Python 多次定义函数时，只有最后的定义被使用）
        return


# router 路由
from fastapi import APIRouter

router_access = APIRouter(prefix='/v0/access', tags=['认证'])

@router_access.post('/login')
def login(form: OAuth2PasswordRequestForm = Depends()):
    # 输入和输出：username、password，access_token、token_type 都不需要自己指定键名
    if form.username != config.username:
        raise HTTPException(status_code=400, detail='无效用户')
    if form.password != config.password:
        raise HTTPException(status_code=400, detail='无效密码')

    return {
        'access_token': access.token,
        'token_type': 'bearer'
    }

@router_access.get('/user-info')
def user_info(token: str = Depends(check_token)):
    return config.username
