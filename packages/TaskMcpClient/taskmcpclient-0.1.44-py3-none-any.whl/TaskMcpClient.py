# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250428-104133
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
启动MCP客户端，执行聊天(chat)或任务(task)
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, PrintAndSleep
import os
import asyncio

from InvokeMcpServer import InvokeMcpServer
from LlmServer import LlmServer
from FileQueryResult import FileQueryResult


class TaskMcpClient:

    def __init__(self, sEnvFN='.env', sRunMode='task'):
        self.sRunMode = sRunMode
        self.sWorkDir = os.getcwd()
        PrintTimeMsg(f'TaskMcpClient.sWorkDir={self.sWorkDir}=')

        self.oIMS = InvokeMcpServer(self.sWorkDir)

        self.oLlm = LlmServer(self.sWorkDir, sEnvFN)

    async def _loop_chat(self):
        # MCP聊天
        async def callBackLlm(sQuery):
            # 返回 Llm 请求结果
            PrintTimeMsg(f"callBackLlm.sQuery={sQuery}=")
            return await self.oLlm.process_query(sQuery,
                                                self.oIMS.lsServFuncTools,
                                                self.oIMS.call_mcp_func_sqids,
                                                self.oIMS.dictSchemaBySqids)
        try:
            await self.oIMS.connect_mcp_servers()
            await self.oIMS.loop_mcp_chat(callBackLlm)
        finally:
            await self.oIMS.cleanup()

    async def _loop_task(self):
        # MCP循环监听处理文件请求
        PrintTimeMsg("_loop_task.MCP Client Started!")

        async def callBackLlm(sQuery):
            # 返回 oLlm，由 oFile 处理
            PrintTimeMsg(f"callBackLlm.sQuery={sQuery}=")
            await self.oLlm.process_query(sQuery,
                                          self.oIMS.lsServFuncTools,
                                          self.oIMS.call_mcp_func_sqids,
                                          self.oIMS.dictSchemaBySqids)
            return self.oLlm

        self.oFile = FileQueryResult(self.sWorkDir)

        iLoopCnt = 0
        while True:
            iSleepSeconds = 60
            try:
                lsNoExtFN = self.oFile.list_file_query_task()
                if lsNoExtFN:
                    await self.oIMS.connect_mcp_servers()
                    for sNoExtFN in lsNoExtFN:
                        await self.oFile.deal_file_query_result(sNoExtFN, callBackLlm)
            except Exception as e:
                PrintTimeMsg(f"_loop_task.e={repr(e)}=")
            finally:
                await self.oIMS.cleanup()
            PrintAndSleep(iSleepSeconds, f'_loop_task.iLoopCnt={iLoopCnt}', iLoopCnt % 10 == 0)
            iLoopCnt += 1

    async def loop_chat_task(self, sRunMode):
        # MCP循环，不同模式
        if sRunMode == 'chat':
            await self._loop_chat()
        else:
            await self._loop_task()


async def mainTaskMcpClient():
    sRunMode = 'chat'  # 默认是聊天模式
    sEnvFN = '.env'  # 环境变量配置文件
    if len(sys.argv) >= 2:
        sRunMode = sys.argv[1]
        if len(sys.argv) >= 3:
            sEnvFN = sys.argv[2]
    oTMC = TaskMcpClient(sEnvFN, sRunMode)
    await oTMC.loop_chat_task(sRunMode)


def asyncio_loop_run(cbASyncFunc):
    # 循环等待执行异步IO函数
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cbASyncFunc())


def main():
    asyncio_loop_run(mainTaskMcpClient)


if __name__ == '__main__':
    main()
