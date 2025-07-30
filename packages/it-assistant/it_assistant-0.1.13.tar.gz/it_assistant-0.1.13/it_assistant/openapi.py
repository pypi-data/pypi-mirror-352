# -*- coding: utf-8 -*-


import copy
import csv
import time

import requests
import json
from typing import List, Dict


def get_SegSearchCandidates(Query: str, Candidates: List[Dict]) -> str or None:
    """
    获取分段搜索候选结果。

    :param Query: 搜索查询字符串
    :param Candidates: 候选结果列表，每个元素是一个字典，包含 "Score", "Text", "Attrs" 等键
    :return: 按分数排序后的前 5 个候选结果的 JSON 字符串，如果请求失败则返回 None
    """
    api_url = "https://genie.bytedance.com/pre/entsol/genie/skills/it-service/common/SegSearchCandidates"
    payload = {
        "Query": Query,
        "TopN": 0,
        "Candidates": Candidates
    }

    headers = {
        'Authorization': 'Basic bWFzLTZrMGJxLWgwMmhxbDM4MjQtMzJrcXQ6YTljNDIwMWJlOTc4OTg4MDRhZmZiNTQyMzA2ZTMxMzU=',
        'Content-Type': 'application/json'
    }

    try:
        # 发起 POST 请求
        response = requests.post(api_url, headers=headers, json=payload)
        # 检查响应状态码
        response.raise_for_status()
        result = response.json()
        if result and 'Candidates' in result:
            top_5_scores = sorted(result['Candidates'], key=lambda x: x.get('Score', 0), reverse=True)[:5]
            return json.dumps(top_5_scores, ensure_ascii=False)
    except requests.RequestException as e:
        print(f"请求发生错误: {e}")
    except (KeyError, ValueError) as e:
        print(f"处理响应数据时发生错误: {e}")

    return None


def get_query_vector(para, clientinfo):
    url = "https://open-itam-mig-pre.bytedance.net/v1/query_vector"
    payload = json.dumps(para)
    headers = {
        'Authorization': clientinfo.get(
            "authorization") or "Basic cm40cmFpdTRwenY1cGlsYTo2bWhvOXV3ZXFrOHZpbDllcXRxMHZ1YmVnc2xjeXBucg==",
        'x-use-ppe': '1',
        'x-tt-env': clientinfo.get("x_tt_env") or "ppe_cn_env_self_test_feat_cr_a",
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def get_by_AssetModelBizTypes(param,res):
    """
    根据AssetModelBizTypes对分数进行预处理
    """
    num = len(param.get("AssetModelFieldsWithOr"))
    res0 =res["body"]["Results"]
    for i in res0:
        i['Score']=i['Score']/num
    res["body"]["Results"]=res0
    return res




def software_asset_sku_structure(QueryValue):
    """
    { "asset_name": "figma", "version": null, "usage": "画画", "other_software": null, "link": "https://www.figma.com" }
    """
    AssetModelFieldsWithAnd = []
    if QueryValue.get('asset_name'):
        AssetModelFieldsWithAnd.append(
            {"FieldName": "vec_neme", "FieldType": "knn", "QueryValue": QueryValue.get("asset_name")})
    if QueryValue.get('version'):
        AssetModelFieldsWithAnd.append(
            {"FieldName": "vec_version", "FieldType": "knn", "QueryValue": QueryValue.get("version")})
    if QueryValue.get('usage'):
        AssetModelFieldsWithAnd.append(
            {"FieldName": "vec_description", "FieldType": "knn", "QueryValue": QueryValue.get("usage")})

    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.6,
        "AssetModelFieldsWithAnd": AssetModelFieldsWithAnd,
        "AssetModelBizTypes": "software_asset_sku"
    }
    return parm


def asset_sku_structure(QueryValue):
    """
    //除4
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword_parts = [QueryValue.get(key, "") for key in ["asset_name", "brand", "model", "specification"] if
                     QueryValue.get(key)]
    keyword = ''.join(keyword_parts)
    keyword = QueryValue['asset_name']
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_brand",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_specification",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_model_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "AssetModelBizTypes": ["asset_sku"]
    }
    return parm


def asset_spu_structure(QueryValue):
    """
    //
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword = QueryValue['asset_name']
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "AssetModelBizTypes": [
            "asset_spu"
        ]
    }
    return parm


def accessory_sku_structure(QueryValue):
    """
    //除2
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """
    keyword = QueryValue['asset_name']
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_brand",
                "FieldType": "knn",
                "QueryValue": [keyword]
            },
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [keyword]
            }
        ],
        "AssetModelBizTypes": ["accessory_sku"]
    }
    return parm


def equipmentrequest_structure(QueryValue,asset_type):
    """
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """

    if "asset_sku" in asset_type:
        return asset_sku_structure(QueryValue)
    if "asset_spu" in asset_type:
        return asset_spu_structure(QueryValue)
    if "accessory_sku" in asset_type:
        return accessory_sku_structure(QueryValue)





def equipmentrequest_structure0(QueryValue):
    """
    {"asset_name": "pc笔记本", "apply_num": 1, "device_type": "asset", "brand": "Xiaomi", "model": "MiBook", "specification": null }
    """

    if QueryValue.get("device_type") and QueryValue.get("device_type")=="asset":
        if QueryValue.get("brand") or QueryValue.get("model") or QueryValue.get("specification"):
            return asset_sku_structure(QueryValue)  #sku
        else:
            return asset_spu_structure(QueryValue)
    else:
        return accessory_sku_structure(QueryValue)




def equipmentreturn_structure(QueryValue):
    """
    设备退还时的请求参数
    """
    parm = {
        "From": 0,
        "Size": 10,
        "MinScore": 0.1,
        "AssetModelFieldsWithOr": [
            {
                "FieldName": "vec_name",
                "FieldType": "knn",
                "QueryValue": [
                    QueryValue.get("asset_name")
                ]
            }
        ],
        "AssetModelBizTypes": [
            "accessory_sku"
        ]
    }
    return parm



if __name__ == '__main__':
    info = {
        'input': {'用户输入/userInput': 'Autodesk 3Ds MAX'},
        'output': {'用户输入/output': 'Autodesk 3Ds MAX'},
        'rt': True,
        'label': []

    }
    info_list = []
    a = 0
    # 读取文件it_assistant/data/software_spu.csv
    with open('data/software_spu.csv', 'r', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['name_zh'] != "--":
                a = a + 1

                row_ = row['name_zh'].lower()
                row_ = row_.replace(' ', '')
                info['input'] = {'用户输入/userInput': row['name_zh']}
                info['output'] = {'用户输入/output': row_}
                res = json.loads(get_query_vector(0.6, [row_], 4, "vec_name"))
                for i in res['body']['Results']:
                    info['label'].append({'socre': i['Score'], 'label': i['Item']['name_zh']})
                print(a)
            info_list.append(copy.deepcopy(info))
            # 将info_list写入本地文件
        # 异常报错或退出时将info_list写入本地文件

    with open('test_data/software_spu_res_xiaoxie.csv', 'w', encoding='utf-8') as file:
        json.dump(info_list, file, ensure_ascii=False)
