数字桌搭：核心代码 core

# config
数字桌搭后端的主要配置
- 区别于 feature 中 conf 开头的配置，更新需要重启后端


# locale
本地化

使用：
- 1、_t('translate')
- 2、i18n：translate: 翻译
- 3、效果：_t('translate') = '翻译'


# standard
数字桌搭的错误和异常与 Python 中的不同，更类似于 Go 语言
- 桌设错误：可以预测的问题
- 桌设异常：无法预测，但不会使程序崩溃

日志：编码 utf-8
- INFO     信息
- WARNING  警告
- ERROR    错误：桌设异常以错误打印
- CRITICAL 崩溃


# text file
文本文件

使用：
- 打开/关闭：不依靠调用方管理 None 状态
- 读取/写入：
    - 每次读取，都会同步内存与硬盘中数据
    - 每次写入，都会检查内存与硬盘中数据，如果不一致则抛出异常
- 撤销/重做


# root path
根路径

使用：将一个文件夹视作根路径，操作文件夹中的文件
