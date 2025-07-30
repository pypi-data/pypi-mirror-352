# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250429-114151
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
监听 task/query 目录下的任务请求文件
调用MCP交互后，将结果放在 task/result 目录下
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, GetCurrentTime
from weberFuncs import JoinGetFileNameFmSrcFile, TryForceMakeDir
import os
import json
import asyncio


class FileQueryResult:
    def __init__(self, sWorkDir=''):
        self.sTaskDir = JoinGetFileNameFmSrcFile(__file__, ['task'], 1)
        # 默认取源码所在目录的上一级目录
        if sWorkDir:  # 赋值了工作目录，则使用工作目录
            self.sTaskDir = os.path.join(sWorkDir, 'task')
        PrintTimeMsg(f'FileQueryResult.sTaskDir={self.sTaskDir}=')
        TryForceMakeDir(os.path.join(self.sTaskDir, 'query'))
        TryForceMakeDir(os.path.join(self.sTaskDir, 'result'))

    async def deal_file_query_result(self, sNoExtFN, callbackQueryResult):
        # 处理一个文件请求，将结果写入文件；并移动文件
        try:
            sFullQueryFN = os.path.join(self.sTaskDir, 'query', f'{sNoExtFN}.md')
            with open(sFullQueryFN, 'r', encoding='utf-8') as f:
                sQueryText = f.read()
                if sNoExtFN.startswith('notify'):
                    try:
                        objectQ = json.loads(sQueryText)
                        sQueryText = objectQ
                    except Exception as e:
                        pass
            try:
                oLlm = await callbackQueryResult(sQueryText)
                # 允许不执行工具函数
                # if oLlm.iToolCallCount <= 0:
                #     PrintTimeMsg(f'deal_file_query_result({sNoExtFN}).oLlm.iToolCallCount={oLlm.iToolCallCount}=')
                #     return False
                if not oLlm.lsFinalTextOut:
                    PrintTimeMsg(f'deal_file_query_result({sNoExtFN}).oLlm.lsFinalTextOut={oLlm.lsFinalTextOut}=')
                    return False
                sResultText = '\n'.join(oLlm.lsFinalTextOut)
                # 去除 think 标签内容
                iStart = sResultText.find('<think>')
                iEnd = sResultText.rfind('</think>')
                if iStart >= 0 and iEnd >= 0:
                    sResultText = sResultText[iEnd + 8:]
                sTm = GetCurrentTime()
                # _{sTm}  _{sTm}
                # 不追加处理时间，由文件自身修改时间替代
                if isinstance(sQueryText, str):  # notify 不添加输入
                    sResultText = '[%s]%s\n %s' % (sTm, sQueryText, sResultText)
                sFullResultFN = os.path.join(self.sTaskDir, 'result', f'{sNoExtFN}_R.md')
                with open(sFullResultFN, 'w', encoding='utf-8') as f:
                    f.write(sResultText)
                # WeiYF.20250522 按照处理逻辑，最终还是要由LLM总结，无需保留
                # sMcpText = '\n'.join(oLlm.lsMcpTextOut)
                # sFullMcpTextFN = os.path.join(self.sTaskDir, 'result', f'{sNoExtFN}_M.md')
                # with open(sFullMcpTextFN, 'w', encoding='utf-8') as f:
                #     f.write(sMcpText)
                sFullReqBakFN = os.path.join(self.sTaskDir, 'result', f'{sNoExtFN}_Q.md')
                os.rename(sFullQueryFN, sFullReqBakFN)
                PrintTimeMsg(f'deal_file_query_result(sFN={sNoExtFN})=OK!')
                return True
            except Exception as e:
                PrintTimeMsg(f'deal_file_query_result(sFN={sNoExtFN}).e={repr(e)}=')
        except Exception as e:
            PrintTimeMsg(f'deal_file_query_result(sFullQueryFN={sFullQueryFN}).e={repr(e)}=')
        return False

    def list_file_query_task(self):
        # 列出文件请求任务
        lsNoExtFN = []
        sQueryDir = os.path.join(self.sTaskDir, 'query')
        try:
            for sFN in os.listdir(sQueryDir):
                sNoExtFN, sExt = os.path.splitext(sFN)
                if sExt.lower() != '.md':
                    continue
                lsNoExtFN.append(sNoExtFN)
        except Exception as e:
            PrintTimeMsg(f'list_file_query_task().e={repr(e)}=')
        # PrintTimeMsg(f'list_file_query_task.lsNoExtFN={lsNoExtFN}=')
        return lsNoExtFN


def mainFileQueryResult():
    o = FileQueryResult()

    def callbackQueryResult(sRequestText):
        PrintTimeMsg(f"callbackQueryResult.sRequestText={sRequestText}=")
        return f"callbackQueryResult.sResult={sRequestText}=Echo!"

    # o.deal_file_query_result('test', callbackQueryResult)
    o.list_file_query_task()


if __name__ == '__main__':
    mainFileQueryResult()
