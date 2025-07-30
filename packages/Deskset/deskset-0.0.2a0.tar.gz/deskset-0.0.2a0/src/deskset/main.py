# ==== 类型标注 ====
from __future__ import annotations


# ==== 命令行参数 ====
from argparse import ArgumentParser

parser = ArgumentParser(description='数字桌搭后端命令行参数')
parser.add_argument('-dev', action='store_true', help='以开发者环境启动')
args, _ = parser.parse_known_args()  # 忽略 uvicorn 热重载传入的参数

DEVELOP_ENV = args.dev
DEBUG_MODE  = False  # 调试模式


# ==== 确保各模块所需目录存在 ====
from pathlib import Path

Path('./config').mkdir(exist_ok=True)  # 配置 core.config
Path('./logs').mkdir(exist_ok=True)    # 日志 core.log

Path('./i18n').mkdir(exist_ok=True)  # 翻译 core.locale

Path('./api').mkdir(exist_ok=True)  # 插件 router.api


# ==== 日志 ====
from deskset.core.log import logging

if DEVELOP_ENV:
    logging.info('Running on Development Environment')
if DEBUG_MODE:
    logging.info('Open Debug Mode')


# ==== 服务器地址 host 和端口 port ====
from deskset.core.config import config

server_host = config.server_host
server_port = config.server_port
logging.info(f'Server URL is http://{server_host}:{server_port}')


# ==== Lifespan 生命周期 ====
from contextlib import asynccontextmanager

from deskset.feature.note import apscheduler as note_apscheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info('start lifespan')
    note_apscheduler.start()  # 不用 paused=True 暂停，uvicorn.run 自然启停
    yield
    logging.info('finish lifespan')
    note_apscheduler.shutdown()


# ==== FastAPI 应用 ====
# ！！！警告，需要身份验证，不然任意桌面应用程序都能访问本服务器！！！
# 一个 CSRF 示例：<img src="http://127.0.0.1:8000/v0/device/cpu"></img>，可在其他 Electron 程序中访问本服务器接口
from fastapi import FastAPI

app = FastAPI(lifespan=lifespan)


# ==== FastAPI：中间件 ====
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# 仅允许本机访问
  # 对 http 和 websocket 都生效
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1'])


# ==== FastAPI：CORS 跨域请求 ====
  # Vite：http://localhost:1420
  # Tauri：http://tauri.localhost
  # Obsidian：app://obsidian.md
if DEVELOP_ENV:  # 开发时有 Vite Server 需要添加 CORS
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:1420', 'app://obsidian.md'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    logging.info(f'Add http://localhost:1420, app://obsidian.md to CORS')

if not DEVELOP_ENV:  # Tauri 构建后用 http://tauri.localhost 通信...
    from fastapi.middleware.cors import CORSMiddleware

    # 会覆盖上面的 CORS，不要一起用
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://tauri.localhost', 'app://obsidian.md'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    logging.info(f'Add http://tauri.localhost, app://obsidian.md to CORS')


# ==== FastAPI：统一错误（异常）处理 ====
from fastapi.requests import Request
from deskset.core.standard import DesksetError
from fastapi.responses import JSONResponse
from deskset.router.unify import DesksetErrorRep
from http import HTTPStatus

@app.exception_handler(DesksetError)
def deskset_error(request: Request, err: DesksetError):
    return DesksetErrorRep(content=err)

@app.exception_handler(Exception)
def deskset_exception(request: Request, exc: Exception):
    logging.exception(exc, exc_info=exc)
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=str(exc)
    )


# ==== FastAPI Router：认证接口 ====
from deskset.router.unify import router_access
app.include_router(router_access)


# ==== FastAPI Router：调试接口 ====
if DEBUG_MODE:
    from deskset.router.debug import router_debug
    app.include_router(router_debug)


# ==== FastAPI Router：路由注册 ====
from deskset.router.device import router_device
app.include_router(router_device)

from deskset.router.note import router_note
app.include_router(router_note)

from deskset.router.greet import router_greet
app.include_router(router_greet)

from deskset.router.current import router_datetime
app.include_router(router_datetime)

# from deskset.router.cloud import router_cloud
# app.include_router(router_cloud)

from deskset.router.quick import router_quick
app.include_router(router_quick)

from deskset.router.weather import router_weather
app.include_router(router_weather)


# ==== FastAPI Router：插件注册：/api 作为所有插件路由的根路径 ====
from deskset.router.api import router_plugin_root
app.include_router(router_plugin_root)


# 启动服务器
import uvicorn

def main():
    uvicorn.run(app, host=server_host, port=server_port)

# 在这个文件启用 uvicorn.run(reload=True) 会影响 vscode git 检查
