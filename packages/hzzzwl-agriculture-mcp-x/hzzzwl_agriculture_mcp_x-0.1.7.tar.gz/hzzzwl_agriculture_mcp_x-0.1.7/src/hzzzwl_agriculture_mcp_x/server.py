# server.py
import os
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any
import httpx
from datetime import datetime
import json

api_url = "https://report.hzzzwl.com"

# Create an MCP server
mcp = FastMCP("hzzzwl-agriculture-mcp-x")


def post_form_request(url: str, form_data: Dict[str, Any], **kwargs) -> Optional[Dict[str, Any]]:
    """
    发送 x-www-form-urlencoded 格式的 POST 请求，并返回 JSON 响应
    
    :param url: 请求的目标 URL
    :param form_data: 表单参数字典（例如 {"key1": "value1"}）
    :param kwargs: 其他传递给 `httpx.post` 的参数（如 headers、timeout 等）
    :return: 解析后的 JSON 字典，请求失败时返回 None
    """
    try:
        # 发送 POST 请求
        response = httpx.post(
            url,
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            **kwargs
        )
        response.raise_for_status()  # 检查 4xx/5xx 错误
        return response.json()
    
    except httpx.RequestError as e:
        print(f"请求失败: {e}")  # 网络问题（如 DNS 解析失败、连接超时）
    except httpx.HTTPStatusError as e:
        print(f"HTTP 错误: {e.response.status_code} {e.response.text}")  # 状态码非 2xx
    except (ValueError, TypeError) as e:
        print(f"JSON 解析失败: {e}")  # 响应内容不是有效 JSON
    
    return None


def check_token() -> Optional[Dict[str, Any]]:

    api_key = os.getenv("KEY")

    test_url = api_url+"/mcp_server2/cellphone/getData.do?sysCmd=checkToken"
    test_data = {"token": api_key}
    # 发送请求
    result = post_form_request(test_url, test_data)

    return result

@mcp.tool()
def get_now_time() -> Optional[Dict[str, Any]]:
    """获取当前时间"""

    current_time = datetime.now()
    # 格式化时间（自定义输出格式）
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    mjson = {"data":formatted_time,'code':'200','msg':'ok'}
    json_str = json.dumps(mjson, ensure_ascii=False)  # 关键设置
    return json_str,200,{"Content-Type":"application/json","Server":"None"}

@mcp.tool()
def getNyInfo(name:str,djzh:str) -> Optional[Dict[str, Any]]:
    """根据农药名称：name和登记证号：djzh，获得该农药的基本信息,登记证号不必填。
    返回json格式数据，其中list为jsonarray，
    里面包含hzrq：核准日期，ccysff：储存和运输方法，shengCQY：登记证持有人(生产企业)，
    dux：毒性，description：备注，cpxn：产品性能，yxqz：有效期至，nylb：农药类别，
    zxhzrq：重新核准日期，name：农药名称，jix：剂型，zdjjcs：中毒急救措施，bzq：质量保证期，
    djzh：登记证号，zyxcfhl：总有效成分含量，zysx：注意事项，syjsyq：使用技术要求。
    """
    api_key = os.getenv("KEY")
    test_url = api_url+"/zzdata/api/zzdata/getNyInfo.do"
    test_data = {"name": name,"djzh":djzh,"token":api_key,"mdName":"getNyInfo"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def getNyChengF(name:str,djzh:str) -> Optional[Dict[str, Any]]:
    """根据农药名称：name和登记证号：djzh，获得该农药的主要有效成分,登记证号不必填。
    返回json格式数据，其中list为jsonarray，
    里面包含name_cn：有效成分中文名，name_en：有效成分英文名，hanl：有效成分含量。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/zzdata/api/zzdata/getNyChengF.do"
    test_data = {"name": name,"djzh":djzh,"token":api_key,"mdName":"getNyChengF"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def getNyShengCQY(name:str,djzh:str) -> Optional[Dict[str, Any]]:
    """根据农药名称：name和登记证号：djzh，获得该农药的生产企业信息,登记证号不必填。
    返回json格式数据，其中list为jsonarray，
    里面包含name：企业名称，province：企业所在省份，country：企业所在国家，county：企业所在县，
    postcode：邮编，tel：电话，fox：传真，contact：联系人，phone：手机号码，addr：单位地址，
    email：邮箱。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/zzdata/api/zzdata/getNyShengCQY.do"
    test_data = {"name": name,"djzh":djzh,"token":api_key,"mdName":"getNyShengCQY"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def getNyUseInfo(name:str,djzh:str) -> Optional[Dict[str, Any]]:
    """根据农药名称：name和登记证号：djzh，获得该农药的使用范围和使用方法,登记证号不必填。
    返回json格式数据，其中list为jsonarray，
    里面包含crops：作物/场所，fzdx：防治对象，dosage：用药量（制剂量/亩），syff：施用方法。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/zzdata/api/zzdata/getNyUseInfo.do"
    test_data = {"name": name,"djzh":djzh,"token":api_key,"mdName":"getNyUseInfo"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def getNyInfoByScqy(scqy:str) -> Optional[Dict[str, Any]]:
    """根据生产企业名称：scqy，获得该生产企业生产哪些农药。
    返回json格式数据，其中list为jsonarray，里面包含name：农药名称。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/zzdata/api/zzdata/getNyInfoByScqy.do"
    test_data = {"scqy": scqy,"token":api_key,"mdName":"getNyInfoByScqy"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def getFzffByCropFzdx(crop:str,fzdx:str) -> Optional[Dict[str, Any]]:
    """根据农作物名称：crop和病虫害名称：fzdx，获得防治药物及使用方法。
    返回json格式数据，其中list为jsonarray，
    里面包含name：药物名称，dosage：用药量（制剂量/亩），syff：施用方法。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/zzdata/api/zzdata/getFzffByCropFzdx.do"
    test_data = {"crop": crop,"fzdx":fzdx,"token":api_key,"mdName":"getFzffByCropFzdx"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def getPlantWeather(plant:str) -> Optional[Dict[str, Any]]:
    """根据农作物名称：plant，获得该农作物适合的种植气候以及包含城市。
    返回json格式数据，其中list为jsonarray，
    里面包含weather：气候，city：城市。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/zzdata/api/zzdata/getPlantWeather.do"
    test_data = {"plant": plant,"token":api_key,"mdName":"getPlantWeather"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def getCityWeather(city:str) -> Optional[Dict[str, Any]]:
    """根据城市名称：city，获得该城市的气候以及适合种植的作物。
    返回json格式数据，其中list为jsonarray，
    里面包含weather：气候，plant：作物。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/zzdata/api/zzdata/getCityWeather.do"
    test_data = {"city": city,"token":api_key,"mdName":"getCityWeather"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result


@mcp.tool()
def get_medication_value(productName:str,medicationName:str) -> Optional[Dict[str, Any]]:
    """根据农产品名称：productName和药物名称：medicationName，获得该农产品上的该药物的检出限(检出上限)。
    返回json格式数据，其中list为jsonarray，里面包含unit：单位，pd：检出限，aname：药物名称，name：农产品名称
    ，value：检出限具体的值。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/mcp_server2/cellphone/getData.do?sysCmd=getJcx"
    test_data = {"cpname": productName,"ypname":medicationName,"token":api_key,"mdName":"get_medication_value"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result


@mcp.tool()
def get_monitor_info(areaName: str,cpname:str,year:int) -> Optional[Dict[str, Any]]:
    """根据区划：areaName，农产品名称：cpname，年度：year，获得该地区该农产品的检测合格率。其中年度不必填。
    返回json格式数据，其中list为jsonarray，里面包含year:年度,all_num:抽样批次数量，qualified_num：合格批次数量，qualified_rat：合格率，
    unqualified：不合格数量。"""

    api_key = os.getenv("KEY")
    test_url = api_url+"/mcp_server2/cellphone/getData.do?sysCmd=getHgl"
    test_data = {"areaName": areaName, "cpname": cpname,"year":year,"token":api_key,"mdName":"get_monitor_info"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def get_risk_agricultural_products(areaName: str,year:int) -> Optional[Dict[str, Any]]:
    """根据区划：areaName，年度：year，获得该地区检测合格率较低的农产品(风险农产品)。
    返回json格式数据，其中list为jsonarray，里面包含sampid:产品id,name:产品名称，zcs：抽检数量，cs：不合格数量。"""

    api_key = os.getenv("KEY")
    test_url = api_url+"/mcp_server2/cellphone/getData.do?sysCmd=getFxpz"
    test_data = {"areaName": areaName, "year":year,"token":api_key,"mdName":"get_risk_agricultural_products"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def get_hgz_num(areaName: str,year:int,cpname:str) -> Optional[Dict[str, Any]]:
    """根据区划：areaName，年度：year，cpname:产品名称，获得该地区合格证开具批次数量。其中：年度和产品名称不必填。
    返回json格式数据，其中list为jsonarray，里面包含year:年度,num:批次，dyzs：打印张数。"""

    api_key = os.getenv("KEY")
    test_url = api_url+"/mcp_server2/cellphone/getData.do?sysCmd=getHgzNum"
    test_data = {"areaName": areaName, "year":year,"cpname":cpname,"token":api_key,"mdName":"get_hgz_num"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result


@mcp.tool()
def get_sale_buy_num(areaName: str,name:str,year:int) -> Optional[Dict[str, Any]]:
    """根据区划：areaName和农资产品名称或者分类：name，年度：year,获得该地区该农资产品的进货量和销售量。其中年度不必填。
    返回json格式数据，其中list为jsonarray，里面包含year：年份,totalBuy：进货量kg，totalSale：销售量kg。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/mcp_server1/api/zzchat/sale_buy_num.do"
    test_data = {"areaName": areaName, "name": name,"year":year,"token":api_key,"mdName":"get_sale_buy_num"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result


@mcp.tool()
def getNzdByYpName(areaName: str,name:str) -> Optional[Dict[str, Any]]:
    """根据区划：areaName和农资产品名称：name，获得该地区售卖该农资产品的农资店信息和农资产品信息。
    比如：用户想知道哪里可以购买到某某农资产品，可以使用该工具。
    返回json格式数据，其中list为jsonarray，里面包含nzdname：农资店名称,nzdaddress：农资店地址，
    nzdlxdh：农资店联系电话，name：农资产品名称，guig：农资产品规格，price：农资产品价格，
    xl：农资产品销量，kc：农资产品库存。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/mcp_server1/api/zzchat/getNzdByYpName.do"
    test_data = {"areaName": areaName, "name": name,"token":api_key,"mdName":"getNzdByYpName"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result


@mcp.tool()
def getZtfp(areaName: str,year:int) -> Optional[Dict[str, Any]]:
    """根据区划：areaName和年度：year,获得该地区主推配方肥流通量。其中年度不必填。
    返回json格式数据，其中list为jsonarray，里面包含year：年份,at：流通量(吨)。"""
    api_key = os.getenv("KEY")
    test_url = api_url+"/mcp_server1/api/zzchat/getZtfp.do"
    test_data = {"areaName": areaName, "year":year,"token":api_key,"mdName":"getZtfp"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result


@mcp.tool()
def get_agricultural_guidance_vector(text: str) -> Optional[Dict[str, Any]]:
    """根据用户的问题：text从农事指导的向量库中查找出几段最近似的内容，需要你归纳总结形成答案给用户。
    返回json格式数据，其中data为jsonarray，里面包含content：近似的内容。
    从content中选取跟用户的问题相关的内容总结后返回给用户，无关的舍弃不要。
    """
    api_key = os.getenv("KEY")
    test_url = api_url+"/getNszdContent"
    test_data = {"text": text,"token":api_key,"tag":"nszd","mdName":"get_agricultural_guidance_vector"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def get_agricultural_disease_report_vector(text: str) -> Optional[Dict[str, Any]]:
    """根据用户的问题：text从病虫测报的向量库中查找出几段最近似的内容，需要你归纳总结形成答案给用户。
    返回json格式数据，其中data为jsonarray，里面包含content：近似的内容。
    从content中选取跟用户的问题相关的内容总结后返回给用户，无关的舍弃不要。
    """
    api_key = os.getenv("KEY")
    test_url = api_url+"/getNszdContent"
    test_data = {"text": text,"token":api_key,"tag":"bccb","mdName":"get_agricultural_disease_report_vector"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def get_agricultural_case_vector(text: str) -> Optional[Dict[str, Any]]:
    """根据用户的问题：text从农业典型案件的向量库中查找出几段最近似的内容，需要你归纳总结形成答案给用户。
    返回json格式数据，其中data为jsonarray，里面包含content：近似的内容。
    从content中选取跟用户的问题相关的内容总结后返回给用户，无关的舍弃不要。
    """
    api_key = os.getenv("KEY")
    test_url = api_url+"/getNszdContent"
    test_data = {"text": text,"token":api_key,"tag":"nydxal","mdName":"get_agricultural_case_vector"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result

@mcp.tool()
def get_agricultural_growth_model_vector(text: str) -> Optional[Dict[str, Any]]:
    """根据用户的问题：text从农作物生长模式(如：生长环境选择，品种选择，生长期注意事项等)的向量库中查找出几段最近似的内容，需要你归纳总结形成答案给用户。
    返回json格式数据，其中data为jsonarray，里面包含content：近似的内容。
    从content中选取跟用户的问题相关的内容总结后返回给用户，无关的舍弃不要。
    """
    api_key = os.getenv("KEY")
    test_url = api_url+"/getNszdContent"
    test_data = {"text": text,"token":api_key,"tag":"szms","mdName":"get_agricultural_growth_model_vector"}
    
    # 发送请求
    result = post_form_request(test_url, test_data)
    return result


def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()