# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250427-105337
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
封装MCP场景下的LLM服务
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, PrettyPrintStr
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
# import xmltodict
from JsonSchemaValidate import JsonSchemaValidate


class LlmServer:
    def __init__(self, sWorkDir='', sEnvFN='.env'):
        # PrintTimeMsg('LlmServer.__init__')
        sFullEnvFN = sEnvFN
        if sWorkDir:
            sFullEnvFN = os.path.join(sWorkDir, sEnvFN)
        bLoad = load_dotenv(dotenv_path=sFullEnvFN, verbose=True)  # load environment variables from .env
        PrintTimeMsg(f"LlmServer.load_dotenv({sFullEnvFN})={bLoad}")
        sOpenAiUrl = os.getenv("OPENAI_BASE_URL")
        sOpenAiKey = os.getenv("OPENAI_API_KEY")
        self.sOpenAiModel = os.getenv("OPENAI_MODEL")
        PrintTimeMsg(f'LlmServer.sOpenAiUrl={sOpenAiUrl}, sOpenAiModel={self.sOpenAiModel}')
        self.openai = OpenAI(api_key=sOpenAiKey, base_url=sOpenAiUrl)  # 兼容 OpenAI 客户端

    async def get_llm_response(self, lsMsg, lsTools):
        # 向 LLM 发起query请求
        if lsTools:
            PrintTimeMsg(f'get_llm_response(len(lsMsg)={len(lsMsg)},len(lsTools)={len(lsTools)})...')
            response = self.openai.chat.completions.create(
                model=self.sOpenAiModel,
                # max_tokens=1000,
                messages=lsMsg,
                tools=lsTools,
            )
        else:
            PrintTimeMsg(f'get_llm_response(len(lsMsg)={len(lsMsg)},lsTools={lsTools})...')
            response = self.openai.chat.completions.create(
                model=self.sOpenAiModel,
                # max_tokens=1000,
                messages=lsMsg,
            )
        PrintTimeMsg(f'get_llm_response(len(lsMsg)={len(lsMsg)}).response={response}')
        return response

    async def _exec_llm_query_response(self, callbackTool, lsMsg, lsTools, dictSchema):
        # 执行一次LLM请求响应
        response = await self.get_llm_response(lsMsg, lsTools)  # 处理消息
        for choice in response.choices:
            message = choice.message
            if not message.tool_calls:  # 如果不调用工具，则添加到 lsFinalTextOut 中
                self.lsFinalTextOut.append(message.content)
            else:  # 如果是工具调用，则获取工具名称和输入
                for tool_call in message.tool_calls:
                    # tool_name = message.tool_calls[0].function.name
                    tool_func = tool_call.function
                    tool_name = tool_func.name
                    try:
                        dictSch = dictSchema.get(tool_name, {})
                        oJSV = JsonSchemaValidate(dictSch)
                        dictArgv = json.loads(tool_func.arguments)
                        dictRet = oJSV.format_and_validate(dictArgv)
                        tool_args = dictRet
                    except Exception as e:
                        PrintTimeMsg(f"process_query.json_argv.e={repr(e)}=")
                        tool_args = {}
                    PrintTimeMsg(f'process_query.tool_name={tool_name},tool_args={tool_args}=')
                    try:
                        oResult = await callbackTool(tool_name, tool_args)
                        # await self.parse_tool_call_result(oResult)
                        PrintTimeMsg(f"_callbackTool.oResult.isError={oResult.isError}=")
                        if oResult.isError:
                            PrintTimeMsg(f"_callbackTool.oResult.content={oResult.content}=")
                            continue

                        self.iToolCallCount += 1

                        PrintTimeMsg(f"_callbackTool.len(oResult.content)={len(oResult.content)}=")
                        # iContentCnt = 0
                        for oContent in oResult.content:
                            # PrintTimeMsg(f"_callbackTool.oContent={PrettyPrintStr(oContent)}=")
                            # try:
                            #     sXmlStr = '<root>%s</root>' % oContent.text
                            #     dictRoot = xmltodict.parse(sXmlStr, encoding='utf-8')
                            #     dictData = dictRoot.get('root', {})
                            #     iContentCnt += 1
                            #     if 'title' in dictData:
                            #         sTitle = dictData.get('title', '')
                            #         sLink =  dictData.get('link', '')
                            #         sAuthor =  dictData.get('author', '')
                            #         sMdText = f"""- [{sTitle}]({sLink}) By: {sAuthor}"""
                            #     else:
                            #         lsT = []
                            #         lsT.append('')  # 多一条换行
                            #         lsT.append(f'- 第{iContentCnt}条内容')
                            #         for k,v in dictData.items():
                            #             lsT.append(f'  - {k}={v}')
                            #         sMdText = '\n'.join(lsT)
                            #     # PrintTimeMsg(f"_callbackTool.sMdText={sMdText}=")
                            # except Exception as e:
                            #     PrintTimeMsg(f"_exec_llm_query_response.parse.e={repr(e)}=")
                            #     sMdText = oContent.text
                            sMdText = oContent.text
                            self.lsMcpTextOut.append(sMdText)
                    except Exception as e:
                        PrintTimeMsg(f"_exec_llm_query_response.e={repr(e)}=")
                        # return

                    # PrintTimeMsg(f"_exec_llm_query_response.message.content={message.content}=")
                    # 继续与工具结果进行对话
                    if message.content:  # and hasattr(message.content, 'text'):
                        lsMsg.append({
                            "role": "assistant",
                            "content": message.content
                        })
                    # 将工具调用结果添加到消息
                    lsMsg.append({
                        "role": "user",
                        "content": oResult.content
                    })
        if lsTools:  # 在完成工具调用后，再次获取LLM响应，此时不再提供工具
            await self._exec_llm_query_response(callbackTool, lsMsg, None, dictSchema)
        # 前面如果不是工具调用，则直接返回

    async def process_query(self, sQuery: str, lsTools: list, callbackTool, dictSchema):
        # 使用 OpenAI 和可用工具处理查询
        # callbackTool: Callable[[str, list], str]
        # WeiYF 严格声明函数原型，会增加python代码的复杂性，在应用开发中不提倡

        # 创建消息列表
        lsMsg = [
            # {"role": "system", "content": """In this environment you have access to a set of tools you can use to answer the user's question. You can use one tool per message, and will receive the result of that tool use in the user's response. You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use.\n\n## Tool Use Formatting\n\nTool use is formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:\n\n<tool_use>\n  <name>{tool_name}</name>\n  <arguments>{json_arguments}</arguments>\n</tool_use>\n\nThe tool name should be the exact name of the tool you are using, and the arguments should be a JSON object containing the parameters required by that tool. For example:\n<tool_use>\n  <name>python_interpreter</name>\n  <arguments>{\"code\": \"5 + 3 + 1294.678\"}</arguments>\n</tool_use>\n\nThe user will respond with the result of the tool use, which should be formatted as follows:\n\n<tool_use_result>\n  <name>{tool_name}</name>\n  <result>{result}</result>\n</tool_use_result>\n\nThe result should be a string, which can represent a file or any other output type. You can use this result as input for the next action.\nFor example, if the result of the tool use is an image file, you can use it in the next action like this:\n\n<tool_use>\n  <name>image_transformer</name>\n  <arguments>{\"image\": \"image_1.jpg\"}</arguments>\n</tool_use>\n\nAlways adhere to this format for the tool use to ensure proper parsing and execution.\n\n## Tool Use Examples\n\nHere are a few examples using notional tools:\n---\nUser: Generate an image of the oldest person in this document.\n\nAssistant: I can use the document_qa tool to find out who the oldest person is in the document.\n<tool_use>\n  <name>document_qa</name>\n  <arguments>{\"document\": \"document.pdf\", \"question\": \"Who is the oldest person mentioned?\"}</arguments>\n</tool_use>\n\nUser: <tool_use_result>\n  <name>document_qa</name>\n  <result>John Doe, a 55 year old lumberjack living in Newfoundland.</result>\n</tool_use_result>\n\nAssistant: I can use the image_generator tool to create a portrait of John Doe.\n<tool_use>\n  <name>image_generator</name>\n  <arguments>{\"prompt\": \"A portrait of John Doe, a 55-year-old man living in Canada.\"}</arguments>\n</tool_use>\n\nUser: <tool_use_result>\n  <name>image_generator</name>\n  <result>image.png</result>\n</tool_use_result>\n\nAssistant: the image is generated as image.png\n\n---\nUser: \"What is the result of the following operation: 5 + 3 + 1294.678?\"\n\nAssistant: I can use the python_interpreter tool to calculate the result of the operation.\n<tool_use>\n  <name>python_interpreter</name>\n  <arguments>{\"code\": \"5 + 3 + 1294.678\"}</arguments>\n</tool_use>\n\nUser: <tool_use_result>\n  <name>python_interpreter</name>\n  <result>1302.678</result>\n</tool_use_result>\n\nAssistant: The result of the operation is 1302.678.\n\n---\nUser: \"Which city has the highest population , Guangzhou or Shanghai?\"\n\nAssistant: I can use the search tool to find the population of Guangzhou.\n<tool_use>\n  <name>search</name>\n  <arguments>{\"query\": \"Population Guangzhou\"}</arguments>\n</tool_use>\n\nUser: <tool_use_result>\n  <name>search</name>\n  <result>Guangzhou has a population of 15 million inhabitants as of 2021.</result>\n</tool_use_result>\n\nAssistant: I can use the search tool to find the population of Shanghai.\n<tool_use>\n  <name>search</name>\n  <arguments>{\"query\": \"Population Shanghai\"}</arguments>\n</tool_use>\n\nUser: <tool_use_result>\n  <name>search</name>\n  <result>26 million (2019)</result>\n</tool_use_result>\nAssistant: The population of Shanghai is 26 million, while Guangzhou has a population of 15 million. Therefore, Shanghai has the highest population.\n\n\n## Tool Use Available Tools\nAbove example were using notional tools that might not exist for you. You only have access to these tools:"""},
            # {"role": "user", "content": sQuery},
        ]
        if isinstance(sQuery, list):  # notify
            for dictQ in sQuery:
                sContent = dictQ.get('sContent', '')
                if sContent:
                    lsMsg.append({"role": "user", "content": sContent})
        elif isinstance(sQuery, str):  # query
            lsMsg.append({"role": "user", "content": sQuery})
        else:
            lsMsg.append({"role": "user", "content": str(sQuery)})

        self.lsFinalTextOut = []  # LLM最终返回结果
        self.lsMcpTextOut = []  # McpServer返回结果
        self.iToolCallCount = 0
        await self._exec_llm_query_response(callbackTool, lsMsg, lsTools, dictSchema)
        sResultMcpTextOut = '\n'.join(self.lsFinalTextOut)
        return sResultMcpTextOut

    # async def call_mcp_func(self, tool_name, tool_args, callbackTool):
    #     # 直接调用MCP服务端函数，用于测试
    #     self.lsMcpTextOut = []  # McpServer返回结果
    #     self.iToolCallCount = 0
    #     oResult = await callbackTool(tool_name, tool_args)
    #     for oContent in oResult.content:
    #         sMdText = oContent.text
    #         self.lsMcpTextOut.append(sMdText)
    #     return self


def mainLlmServer():
    import asyncio
    o = LlmServer()
    lsMessages = [{
        'role': 'user',
        'content': '天为什么蓝色的？'
    }]
    o.get_llm_response(lsMessages, [])
    asyncio.run(o.process_query('天为什么蓝色的？', [], callbackTool, {}))

    # # async def callbackTool(sName, dictArgs):
    # #     from weberFuncs import CObjectOfDict
    # #     PrintTimeMsg(f"callbackTool(sName={sName}, dictArgs={dictArgs})")
    # #     oResult = CObjectOfDict({
    # #         'content': [
    # #             CObjectOfDict({
    # #                 'text': f"callbackTool(sName={sName}, dictArgs={dictArgs})",
    # #             }),
    # #         ]
    # #     })
    # #     return oResult
    # asyncio.run(o.call_mcp_func('get_tool_name', {'foo': 'bar'}, callbackTool))



if __name__ == '__main__':
    mainLlmServer()
