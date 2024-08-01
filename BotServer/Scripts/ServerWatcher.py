import asyncio
from threading import Thread

from nonebot.log import logger

from .Config import config
from .Managers import server_manager


class ServerWatcher(Thread):
    cpus: dict[str, list] = {}
    rams: dict[str, list] = {}

    def __init__(self):
        Thread.__init__(self, name='ServerWatcher', daemon=True)

    def run(self):
        logger.info('服务器监视线程启动。')
        asyncio.run(self.main_loop())

    async def main_loop(self):
        while True:
            logger.debug('定时获取更新服务器信息。')
            data = await self.get_occupation_data()
            for name, (cpu, ram) in data.items():
                if len(self.cpus[name]) > config.server_watcher_max_cache:
                    self.cpus[name].pop(0)
                    self.rams[name].pop(0)
                self.cpus[name].append(cpu)
                self.rams[name].append(ram)
            await asyncio.sleep(config.server_watcher_update_interval)

    def remove_server(self, name: str):
        self.cpus.pop(name, None)
        self.rams.pop(name, None)

    @staticmethod
    async def get_occupation_data():
        data = {}
        for name, server in server_manager.servers.items():
            data[name] = await server.send_server_occupation()
        return data


server_watcher = ServerWatcher()
