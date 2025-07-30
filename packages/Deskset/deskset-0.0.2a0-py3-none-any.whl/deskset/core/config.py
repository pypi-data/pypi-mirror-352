from __future__ import annotations
from typing import Optional

import json

from deskset.core.log import logging

CONFIG_MAIN_PATH = './config/deskset.json'
CONFIG_MAIN_ENCODE = 'utf-8'


# ==== 读取 config/deskset.json 中的配置 ====
  # - [ ] 需要换名 + 移至其他文件
class Config(object):
    _instance: Optional[Config] = None

    def __new__(cls) -> Config:
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self._instance, '_is_init'):
            self._is_init = True
            self._init_once()

    def _init_once(self) -> None:
        # 1、属性设为默认值
        # 2、读取，检查通过后修改属性
        # 3、写入，属性覆盖上一步无效配置
        # 注意！不要添加跟配置无关的公有成员属性，此类依靠自身属性读取 json 配置

        # === 默认值 ===
        # 语言和编码
        self.language: str = 'zh-cn'
        self.encoding: str = 'utf-8'
        # 端口
        self.server_host: str = '127.0.0.1'
        self.server_port: int = 6527
        self.noteapi_host: str = '127.0.0.1'
        self.noteapi_port: int = 6528  # DesksetNoteAPI 插件端口
        # 用户和密码：self.username 和 self.password 每次都随机生成，读取配置文件成功再被覆盖
        import random
        import string
        letters_and_digits = string.ascii_letters + string.digits
        self.username: str = 'deskset-user' + ''.join(random.choices(letters_and_digits, k=random.randint(5, 10)))
        self.password: str = 'deskset-pswd' + ''.join(random.choices(letters_and_digits, k=random.randint(10, 20)))

        # === 读取 ===
        try:
            with open(CONFIG_MAIN_PATH, 'r', encoding=CONFIG_MAIN_ENCODE) as file:
                data: dict = json.load(file)

                for attr_key, attr_value in list(self.__dict__.items()):  # list 创建副本后修改 self 属性
                    # 不是私有成员属性
                    if attr_key.startswith('_'):
                        continue

                    # 配置类型跟默认值一致
                    config_key = attr_key.replace('_', '-')
                    config_type = type(attr_value)
                    if type(data.get(config_key)) != config_type:
                        continue

                    # 修改属性。注：setattr 不会丢掉类型检查
                    value = data.get(config_key)
                    if   config_type == type(10000):
                        setattr(self, attr_key, value)
                    elif config_type == type('str') and value != '':
                        setattr(self, attr_key, value)
                    else:
                        pass
        except FileNotFoundError:
            logging.warning(f'{CONFIG_MAIN_PATH} not found')
            pass
        except json.JSONDecodeError:
            logging.warning(f'{CONFIG_MAIN_PATH} decode failed')
            pass

        # === 写入 ===
        with open(CONFIG_MAIN_PATH, 'w', encoding=CONFIG_MAIN_ENCODE) as file:
            data: dict = {
                key.replace('_', '-'): value for key, value in self.__dict__.items() if not key.startswith('_')
            }
            json.dump(data, file, ensure_ascii=False, indent=4)


config = Config()


if __name__ == '__main__':
    for attr_key, attr_value in config.__dict__.items():
        print(attr_key, attr_value)


# ==== 配置读写函数 ====
  # 根据实例成员，读写配置
  # _confpath 以 config 作根目录，读写 config/{_confpath}.yaml 文件，编码一律 utf-8
  # _confitem_key = value 对应 key: value 配置项
    # _confitem_custom_prop 下划线将被连字符替换 custom-prop
  # 使用提醒：
    # 成员：self._confXXX（注意 self）
    # 类型提示：class Conf: _confXXX: str（在类中注解）
from pathlib import Path
from typing import get_type_hints, get_args

import yaml

from deskset.core.standard import DesksetError

READ_CONFFILE_ERROR = DesksetError(message='配置文件 {} 读取失败：{}！')


def write_conf_file(instance: object) -> None:
    if getattr(instance, '_confpath', None) is None:
        raise ValueError(f'_confpath not exist in {type(instance)} class')
    relpath = Path('./config') / f'{instance._confpath}.yaml'

    items = {}  # 配置项

    for attr_key, attr_value in list(instance.__dict__.items()):
        if not attr_key.startswith('_confitem_'):
            continue

        key = attr_key[len('_confitem_'):].replace('_', '-')  # [len('_confitem_'):] 去掉 _confitem_
        value = attr_value
        items[key] = value  # Python 3.7+ 开始字典有序

    relpath.parent.mkdir(parents=True, exist_ok=True)  # open 不会创建目录，用 Path 提前创建

    with open(relpath, 'w', encoding='utf-8') as file:
        yaml.dump(items, file, allow_unicode=True, sort_keys=False)  # sort_keys=False 不排序


def read_conf_file(instance: object) -> None:
    if getattr(instance, '_confpath', None) is None:
        raise ValueError(f'_confpath not exist in {type(instance)} class')
    relpath = Path('./config') / f'{instance._confpath}.yaml'

    # 读取文件，异常由调用方处理
      # 可能异常：文件不存在 FileNotFoundError、yaml 解析失败 yaml.YAMLError、yaml 解析非字典 TypeError
    if not relpath.is_file():
        raise READ_CONFFILE_ERROR.insert(relpath, '文件不存在')
    with open(relpath, 'r', encoding='utf-8') as file:
        try:
            items: dict = yaml.safe_load(file)
        except yaml.YAMLError:
            raise READ_CONFFILE_ERROR.insert(relpath, 'YAML 解析失败')

        # 没解析成字典，也算异常
        if not isinstance(items, dict):
            raise READ_CONFFILE_ERROR.insert(relpath, '解析结果不是字典')

        # attr_value 作为配置项默认值
        for attr_key, attr_value in list(instance.__dict__.items()):
            if not attr_key.startswith('_confitem_'):
                continue

            value_type = type(attr_value)
            key = attr_key[len('_confitem_'):].replace('_', '-')
            value = items.get(key, None)

            if type(value) != value_type:  # 值类型 != 配置项默认值类型
                continue

            if   value_type == type(10000):
                setattr(instance, attr_key, value)
            elif value_type == type('str'):
                if value != '':
                    setattr(instance, attr_key, value)
                if value == '':  # 类型标注包含 None = 允许空字符串
                    annotations = get_type_hints(type(instance))
                    if type(None) in get_args(annotations.get(attr_key)):
                        setattr(instance, attr_key, '')


# ==== 配置读写函数（绝对路径） ====
  # 配置路径从绝对路径 _confabspath（包括文件后缀）读取
def write_conf_file_abspath(instance: object, format: str = 'yaml') -> None:
    if getattr(instance, '_confabspath', None) is None:
        raise ValueError(f'_confabspath not exist in {type(instance)} class')
    abspath = Path(instance._confabspath)

    items = {}  # 配置项

    for attr_key, attr_value in list(instance.__dict__.items()):
        if not attr_key.startswith('_confitem_'):
            continue

        key = attr_key[len('_confitem_'):].replace('_', '-')  # [len('_confitem_'):] 去掉 _confitem_
        value = attr_value
        items[key] = value  # Python 3.7+ 开始字典有序

    abspath.parent.mkdir(parents=True, exist_ok=True)  # open 不会创建目录，用 Path 提前创建

    with open(abspath, 'w', encoding='utf-8') as file:
        if format == 'yaml':
            yaml.dump(items, file, allow_unicode=True, sort_keys=False)  # sort_keys=False 不排序
        if format == 'json':
            json.dump(items, file, ensure_ascii=False, indent=4)


def read_conf_file_abspath(instance: object, format: str = 'yaml') -> None:
    if getattr(instance, '_confabspath', None) is None:
        raise ValueError(f'_confabspath not exist in {type(instance)} class')
    abspath = Path(instance._confabspath)

    # 读取文件，异常由调用方处理
      # 可能异常：文件不存在 FileNotFoundError、yaml 解析失败 yaml.YAMLError、yaml 解析非字典 TypeError
    if not abspath.is_file():
        raise READ_CONFFILE_ERROR.insert(abspath, '文件不存在')
    with open(abspath, 'r', encoding='utf-8') as file:
        if format == 'yaml':
            try:
                items: dict = yaml.safe_load(file)
            except yaml.YAMLError:
                raise READ_CONFFILE_ERROR.insert(abspath, 'YAML 解析失败')
        if format == 'json':
            try:
                items: dict = json.load(file)
            except json.JSONDecodeError:
                raise READ_CONFFILE_ERROR.insert(abspath, 'JSON 解析失败')

        # 没解析成字典，也算异常
        if not isinstance(items, dict):
            raise READ_CONFFILE_ERROR.insert(abspath, '解析结果不是字典')

        # attr_value 作为配置项默认值
        for attr_key, attr_value in list(instance.__dict__.items()):
            if not attr_key.startswith('_confitem_'):
                continue

            value_type = type(attr_value)
            key = attr_key[len('_confitem_'):].replace('_', '-')
            value = items.get(key, None)

            if type(value) != value_type:  # 值类型 != 配置项默认值类型
                continue

            if   value_type == type(10000):
                setattr(instance, attr_key, value)
            elif value_type == type('str'):
                if value != '':
                    setattr(instance, attr_key, value)
                if value == '':  # 类型标注包含 None = 允许空字符串
                    annotations = get_type_hints(type(instance))
                    if type(None) in get_args(annotations.get(attr_key)):
                        setattr(instance, attr_key, '')
            elif value_type == type([]):  # 附：可以解析 list[dict] 类型
                if len(value) != 0:
                    setattr(instance, attr_key, value)
                if len(value) == 0:  # 同上，包含 None 允许列表为空
                    annotations = get_type_hints(type(instance))
                    if type(None) in get_args(annotations.get(attr_key)):
                        setattr(instance, attr_key, [])
