# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250429-092633
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
- 从 `mcp.server/<MCP服务端的名称>.<通讯类型>.json` 读取mcp服务端配置
    - 通过更改文件扩展名，可以屏蔽某些MCP服务端
- 从 `mcp.server/cmdPath.env` 中读取uv等命令的全局配置
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, PrettyPrintStr
from weberFuncs import JoinGetFileNameFmSrcFile, TryForceMakeDir
from weberFuncs import dict_load_name_value  #, md5
import os
import json


class LoadMcpServerConfig:
    def __init__(self, sWorkDir=''):
        self.sConfigDir = JoinGetFileNameFmSrcFile(__file__, ['mcp.server'], 1)
        # 默认取源码所在目录的上一级目录
        if sWorkDir:  # 赋值了工作目录，则使用工作目录
            self.sConfigDir = os.path.join(sWorkDir, 'mcp.server')
        PrintTimeMsg(f'LoadMcpServerConfig.sConfigDir={self.sConfigDir}=')
        TryForceMakeDir(self.sConfigDir)
        # self.dictCmdPath = self._load_cmd_path_env()
        self.dictCmdPath = dict_load_name_value(os.path.join(self.sConfigDir, 'cmdPath.env'))
        self.dictMcpServers = self._load_mcp_server_json()

    # 转移到 weberFuncs.dict_load_name_value 以便可以跨项目共享
    # def _load_cmd_path_env(self):
    #     # 加载 cmdPath 配置
    #     dictCmdPath = {}
    #     try:
    #         sFullFN = os.path.join(self.sConfigDir, 'cmdPath.env')
    #         with open(sFullFN, 'r', encoding='utf8') as f:
    #             for sLine in f:
    #                 sLine = sLine.strip()
    #                 if not sLine or sLine.startswith('#') or ('=' not in sLine):
    #                     # 空串没有等号，则是不正常的key=value配置，直接忽略
    #                     continue
    #                 sKey, cSep, sValue = sLine.partition('=')
    #                 if '#' in sValue:  # 剔除行内注释
    #                     sV, cSep, sC = sValue.partition('#')
    #                     sValue = sV
    #                 sKey = sKey.strip()
    #                 sValue = sValue.strip('\'\" \t')  # 删除引号及空白
    #                 if sKey:
    #                     dictCmdPath[sKey] = sValue
    #     except Exception as e:
    #         PrintTimeMsg(f'_load_cmd_path_env({sFullFN}).e={repr(e)}=')
    #     PrintTimeMsg(f'_load_cmd_path_env.dictCmdPath={PrettyPrintStr(dictCmdPath)}=')
    #     return dictCmdPath

    def _load_mcp_server_json(self):
        # 加载 MCP 服务端配置
        dictMcpServers = {}
        try:
            # iModuleCnt = 0  # 模块数目
            for sFN in os.listdir(self.sConfigDir):
                if not sFN.endswith('.json'):
                    continue
                if sFN.startswith('@'):  # @开头标识该MCPServer被注释了
                    continue
                sFullFN = os.path.join(self.sConfigDir, sFN)
                with open(sFullFN, 'r', encoding='utf-8') as f:
                    try:
                        dictData = json.load(f)
                        lsV = sFN.split('.')
                        if len(lsV) >= 3:
                            # iModuleCnt += 1
                            # sName.sType.json
                            sModuName = '.'.join(lsV[:-2])
                            # # sModuName = 'M%s' % (md5(sName)[:6])  # 避免 _- 等干扰
                            # sModuName = 'm%.2d' % (iModuleCnt)  # 直接采用模块计数
                            sType = lsV[-2]
                            dictData['type'] = sType
                            dictMcpServers[sModuName] = dictData
                        else:
                            raise Exception(f'sFN={sFN}=format error!')
                    except json.JSONDecodeError as e:
                        PrintTimeMsg(f'_load_mcp_server_json({sFullFN}).e={repr(e)}=')
        except Exception as e:
            PrintTimeMsg(f'_load_mcp_server_json().e={repr(e)}=')
        PrintTimeMsg(f'_load_mcp_server_json.dictMcpServers={PrettyPrintStr(dictMcpServers)}=')
        return dictMcpServers


def mainLoadMcpServerConfig():
    o = LoadMcpServerConfig()


if __name__ == '__main__':
    mainLoadMcpServerConfig()
