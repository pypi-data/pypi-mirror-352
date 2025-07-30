# ==== 依赖 ====
import psutil

# psutil 拿不到的信息
import ctypes

dll_disk_active_time = ctypes.windll.LoadLibrary('./lib/disk_active_time.dll')
dll_disk_active_time.get.restype = ctypes.c_double



# ==== Win32 设备系统 ====
from threading import Lock, Thread
from time import time, sleep


class Win32Device:
    # --- 实时访问：自动轮询 ---
      # 每隔 self._interval 秒，读取并刷新 self._realtime 一次
    from dataclasses import dataclass

    @dataclass
    class Realtime:
        def __init__(self) -> None:
            self.cpu: dict[str, float] = { 'percent': 0.0 }
            self.ram: dict[str, float] = { 'percent': 0.0 }
            self.disk: dict[str, float] = { 'percent': 0.0 }
            self.network: dict[str, int] = { 'sent': 0, 'recv': 0 }

    def __init__(self, interval: float = 1.0) -> None:
        self._realtime = Win32Device.Realtime()

        self._interval = interval  # 轮询间隔 单位 s
        self._lock = Lock()
        self._loop = Thread(target=self.__loop_refresh)
        self._loop.daemon = True  # 守护线程，主进程结束时自动退出
        self._loop.start()

    def __loop_refresh(self) -> None:
        dll_disk_active_time.start()

        self.__last_net = psutil.net_io_counters()
        self.__last_nettime = time()
        while True:
            sleep(self._interval)

            # *** 芯片 ***
              # 利用率 percent: float %
            self._realtime.cpu['percent'] = psutil.cpu_percent(interval=0)

            # *** 内存 ***
              # 占用率 percent: float %
            self._realtime.ram['percent'] = psutil.virtual_memory().percent

            # *** 硬盘 ***
              # 使用率 percent: float %
                # 注 1：使用率 = 活动时间：单位时间内硬盘使用率，也就是 1s 内读写所用时间 / 1s
                # 注 2：round(, 1) 与 psutil 百分比位数保持一致
            self._realtime.disk['percent'] = round(dll_disk_active_time.get(), 1)

            # *** 网络 ***
              # 发送 sent: int Byte/s、接收 recv: int Byte/s
                # 注 1：Kbps 中 Kb(1000 bit) != KB(1024 Byte)
                # 注 2：Byte / 125 = Kbp
            net = psutil.net_io_counters()
            netnow = time()
            netlong = round(netnow - self.__last_nettime, 1)
            self._realtime.network['sent'] = int((net.bytes_sent - self.__last_net.bytes_sent) / netlong)
            self._realtime.network['recv'] = int((net.bytes_recv - self.__last_net.bytes_recv) / netlong)
            self.__last_net = net
            self.__last_nettime = netnow

        dll_disk_active_time.end()  # - [ ] 暂时无法清理，预期应在 fastAPI 应用结束时执行

    @property
    def realtime(self) -> dict:
        return {
            'cpu': self._realtime.cpu,
            'ram': self._realtime.ram,
            'disk': self._realtime.disk,
            'network': self._realtime.network
        }


    # --- 间隔访问：调用一次，读取一次 ---

    # （硬盘）分区信息
    def partitions(self) -> list[dict]:
        partitions = []

        for partition in psutil.disk_partitions():
            partition_usage = psutil.disk_usage(partition.device)
            partitions.append({
                'root': partition.device,
                'total': partition_usage.total,
                'free': partition_usage.free,
                'percent': partition_usage.percent
            })

        return partitions

    # 电池信息
    def battery(self) -> dict:
        battery = psutil.sensors_battery()

        # 设备可能没有电池：台式机、HTPC
          # 直接返回 正在充电 + 电量 100%，省去错误处理
        if battery is None:
            return { 'isplug': True, 'percent': 100 }

        return {
            'isplug': battery.power_plugged,
            'percent': battery.percent
        }

    # 系统信息
    def system(self) -> dict:
        import platform  # 只有这个函数要用 platform，单独导入

        return {
            'name': platform.node(),
            'system': platform.system(),
            'version': platform.version(),
            'machine': platform.machine()
        }
