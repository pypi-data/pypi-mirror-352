# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250515-155129
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
将结果转为Markdown格式
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, GetSrcParentPath
from markitdown import MarkItDown
import os


class ToMarkItDown:
    def __init__(self):
        PrintTimeMsg('ToMarkItDown.__init__')
        self.markitdown = MarkItDown()


def mainToMarkItDown():
    sFN = 'test_markdown_input.txt'
    sWorkDir = GetSrcParentPath(__file__, True)
    PrintTimeMsg(f'ToMarkItDown.sWorkDir={sWorkDir}=')
    sFullFN = os.path.join(sWorkDir, sFN)
    o = ToMarkItDown()

    oResult = o.markitdown.convert(sFullFN)
    PrintTimeMsg(f'ToMarkItDown.oResult.text_content={oResult.text_content}=')


if __name__ == '__main__':
    mainToMarkItDown()

