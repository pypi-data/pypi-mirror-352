# -*- coding: utf-8 -*-
"""
 __createTime__ = 20250522-113204
 __author__ = "WeiYanfeng"
 __version__ = "0.0.1"

~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
采用 jsonschema 校验LLM生成的函数参数，并进行格式化转换

[JSON Schema 规范（中文版）](https://json-schema.apifox.cn/)
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs
# pip install jsonschema
"""
import sys
from weberFuncs import PrintTimeMsg

# import json
from jsonschema import validate, Draft7Validator
from jsonschema.exceptions import ValidationError


class JsonSchemaValidate:
    def __init__(self, dictSchema):
        # PrintTimeMsg('JsonSchemaValidate.__init__')
        self.dictSchema = dictSchema

    def format_and_validate(self, dictArgv):
        PrintTimeMsg(f"format_and_validate({dictArgv})...")
        try:
            validator = Draft7Validator(self.dictSchema)
            # 执行深度验证并收集所有错误
            errors = list(validator.iter_errors(dictArgv))
            if not errors:
                PrintTimeMsg(f"format_and_validate({dictArgv})=OK!")
                return dictArgv
            PrintTimeMsg(f"format_and_validate()=errors={errors}!")

            dictRet = {}
            for k,v in dictArgv.items():
                dictRet[k] = v
            for k,v in dictArgv.items():
                if k not in self.dictSchema["properties"]:
                    del dictRet[k]
                    PrintTimeMsg(f'format_and_validate()=delete(k={k})!')
                    continue
                sV = str(v).lower()
                lsAnyOf = self.dictSchema["properties"][k]["anyOf"]
                for dictAnyOf in lsAnyOf:
                    sDesc = dictAnyOf['description']
                    sConst = dictAnyOf['const']
                    if sV in sDesc.lower():
                        dictRet[k] = sConst
                        PrintTimeMsg(f'format_and_validate()={v}->{sConst}=!')
                        break
                else:  # 没有在for循环中break
                    sDefault = self.dictSchema["properties"][k].get('default', None)
                    if sDefault:
                        dictRet[k] = sDefault
                        PrintTimeMsg(f'format_and_validate()={v}->{sDefault}=Default!')

            errors = list(validator.iter_errors(dictRet))
            if not errors:
                PrintTimeMsg(f"format_and_validate({dictArgv})=dictRet={dictRet}!")
                return dictRet
            PrintTimeMsg(f"format_and_validate(dictRet={dictRet})=errors={errors}=ReturnNull!")
            for error in errors:
                PrintTimeMsg(f"format_and_validate({dictRet})=❌ {error.validator},{error.message}!")
            return {}
        except ValidationError as e:
            PrintTimeMsg(f"format_and_validate({dictArgv}).e={e.message}=ReturnNull!")
            return {}


def mainClassOne():
   # o = ClassOne()

   # 定义JSON Schema规范
    schema = {
        "type": "object",
        "properties": {
            "category_id": {
                "anyOf": [
                    {
                        "type": "string",
                        "const": "6809637769959178254",
                        "description": "后端"
                    },
                    {
                        "type": "string",
                        "const": "6809637767543259144",
                        "description": "前端"
                    },
                    {
                        "type": "string",
                        "const": "6809635626879549454",
                        "description": "Android"
                    },
                    {
                        "type": "string",
                        "const": "6809635626661445640",
                        "description": "iOS"
                    },
                    {
                        "type": "string",
                        "const": "6809637773935378440",
                        "description": "人工智能"
                    },
                    {
                        "type": "string",
                        "const": "6809637771511070734",
                        "description": "开发工具"
                    },
                    {
                        "type": "string",
                        "const": "6809637776263217160",
                        "description": "代码人生"
                    },
                    {
                        "type": "string",
                        "const": "6809637772874219534",
                        "description": "阅读"
                    }
                ],
                "default": "6809637769959178254"
            }
        },
        "additionalProperties": False,
        "$schema": "http://json-schema.org/draft-07/schema#"
    }


    # 待验证数据
    data_to_validate = {}  # OK
    data_to_validate = {"category_id": "6809637772874219534"}  # OK
    data_to_validate = {"category_id": "6809637772874219535"}  # Error
    data_to_validate = {"category_id": "6809637769959178254"}  # OK Default
    data_to_validate = {"category_id": "阅读", "category_id1": "0"}  # Error to
    data_to_validate = {"category_id": 1, "category_id1": "0"}  # Error to
    data_to_validate = {"category_id": "0"}  # Error -> {} Default
    data_to_validate = {"category_id": ""}  # Error -> {}
    data_to_validate = {"category_id":""}

    oJSV = JsonSchemaValidate(schema)
    oJSV.format_and_validate(data_to_validate)


if __name__ == '__main__':
    mainClassOne()

