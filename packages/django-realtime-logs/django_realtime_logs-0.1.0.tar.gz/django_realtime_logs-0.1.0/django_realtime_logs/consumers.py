import sys
import time
import asyncio
import os

from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        def follow(file_path):
            if sys.platform == "win32":
                import msvcrt
                import ctypes

                file = open(file_path, 'r', encoding="utf-8")
                fd = msvcrt.get_osfhandle(file.fileno())
                ctypes.windll.kernel32.SetFilePointer(fd, 0, None, 2)  # Move to end of file
                return file
            else:
                file = open(file_path, 'r')
                file.seek(0, os.SEEK_END)
                return file

        self.log_file = follow("runtime.log")

        async def tail_log():
            while True:
                line = self.log_file.readline()
                if line:
                    await self.send(line.strip() + '\n')
                await asyncio.sleep(1)

        self.task = asyncio.create_task(tail_log())

    async def disconnect(self, close_code):
        self.task.cancel()
        self.log_file.close()
