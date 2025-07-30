import time
import re
from binascii import b2a_hex, a2b_hex
import requests
import execjs
import ddddocr
from enum import Enum
from typing import Annotated
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    Tool,
    TextContent,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field


class DpipblockTools(str, Enum):
    PORT_ADD = "port_add"
    PORT_DELETE = "port_delete"


def convert_time_to_seconds(time_str: str) -> str:
    """
    将时间字符串转换为秒数
    支持的格式：
    - "永久" 或 "permanent" -> "-1"
    - "1分钟", "1min", "1m" -> "60"
    - "1小时", "1hour", "1h" -> "3600"
    - "1天", "1day", "1d" -> "86400"
    - "1周", "1week", "1w" -> "604800"
    - "1月", "1month" -> "2592000" (30天)
    - "1年", "1year", "1y" -> "31536000"
    - 纯数字 -> 直接返回（假设为秒）
    """
    time_str = time_str.strip().lower()
    
    # 永久封禁
    if time_str in ["永久", "permanent", "forever", "-1"]:
        return "-1"
    
    # 纯数字，直接返回
    if time_str.isdigit():
        return time_str
    
    # 提取数字和单位
    match = re.match(r'(\d+)\s*([a-zA-Z\u4e00-\u9fff]+)', time_str)
    if not match:
        # 如果无法解析，默认返回180秒
        return "180"
    
    number = int(match.group(1))
    unit = match.group(2)
    
    # 时间单位转换表
    time_units = {
        # 分钟
        '分钟': 60, 'min': 60, 'm': 60, 'minute': 60, 'minutes': 60,
        # 小时
        '小时': 3600, 'hour': 3600, 'hours': 3600, 'h': 3600,
        # 天
        '天': 86400, 'day': 86400, 'days': 86400, 'd': 86400,
        # 周
        '周': 604800, 'week': 604800, 'weeks': 604800, 'w': 604800,
        # 月
        '月': 2592000, 'month': 2592000, 'months': 2592000,
        # 年
        '年': 31536000, 'year': 31536000, 'years': 31536000, 'y': 31536000,
        # 秒
        '秒': 1, 'second': 1, 'seconds': 1, 's': 1, 'sec': 1,
    }
    
    multiplier = time_units.get(unit, 1)
    return str(number * multiplier)


def dpfhq_login(username: str, password: str) -> dict:
    with open("7_dpfhq.js", "r", encoding="UTF-8") as file:
        js_code = file.read()
    # 执行 JavaScript 代码
    ctx = execjs.compile(js_code)
    check = ctx.call("valid_refresh")
    uname = ctx.call("conplat_str_encrypt", username)
    pwd = ctx.call("conplat_str_encrypt", password)
    i = 1
    while True:
        if i > 10:
            return None
        url = 'https://10.138.36.249:8889/func/web_main/validate?check=' + check
        main_url_html = requests.get(url=url, verify=False)
        ocr = ddddocr.DdddOcr(show_ad=False)
        image = main_url_html.content
        code = ocr.classification(image)

        pData = ["_csrf_token=4356274536756456326", "uname=" + uname, "ppwd=" + pwd, "language=1", "ppwd1=", "otp_value=",
                 "code=" + code, "check=" + check]
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'slotType=0; SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV; BACKUP_SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV',
            'Host': '10.138.36.249:8889',
            'Referer': 'https://10.138.36.249:8889/html/login.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        url = 'https://10.138.36.249:8889/func/web_main/login_tamper/user/user_login_check_code'
        main_url_html = requests.get(url=url, headers=headers, verify=False)
        response = main_url_html.text
        match = re.search(r'<checkcode>(.*?)</checkcode>', response)
        ycode = match.group(1)
        encryptCode = ctx.call("getEncryptCode", pData, ycode)

        params = {
            '_csrf_token': '4356274536756456326',
            'uname': uname,
            'ppwd': pwd,
            'language': '1',
            'ppwd1': '',
            'otp_value': '',
            'code': code,
            'check': check,
            'encryptCode': encryptCode
        }
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Length': '258',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'slotType=0; SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV; BACKUP_SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV',
            'Host': '10.138.36.249:8889',
            'Origin': 'https://10.138.36.249:8889',
            'Referer': 'https://10.138.36.249:8889/html/login.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        url = 'https://10.138.36.249:8889/func/web_main/login'
        main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
        response = main_url_html.text
        if response.__contains__("校验码验证失败！"):
            i = i + 1
            print("校验码验证失败！")
            time.sleep(1)
            continue
        cookies = main_url_html.cookies
        cookie_list = cookies.get_dict()
        SID = cookie_list.get('SID')

        headers2 = {
            'Accept': 'text/css,*/*;q=0.1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'slotType=0; SID='+SID+'; BACKUP_SID='+SID,
            'Host': '10.138.36.249:8889',
            'Referer': 'https://10.138.36.249:8889/func/web_main/display/frame/main',
            'Sec-Fetch-Dest': 'xslt',
            'Sec-Fetch-Mode': 'same-origin',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        return headers2

def dpfhq_logout(headers):
    url = 'https://10.138.36.249:8889/func/web_main/logout?lang=cn'
    main_url_html = requests.get(url=url, headers=headers, verify=False)

def dpfhq_port_management_getValueId(ip: str, headers: dict) -> str | None:
    params = {
        'searchsips': ip,
        'searchsipe': ip,
        'searchages': 0,
        'searchagee': 31535999,
        'searchact': 0,
        'searchgroups': 128,
        'searchsta': 2,
        'searchgroupname': None
    }
    url = 'https://10.138.36.249:8889/func/web_main/display/maf/maf_addrfilter/maf_cidr_v4_wblist'
    main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
    response = main_url_html.text
    match = re.search(r'<TR VALUE="(.*?)">', response)
    if match:
        ycode = match.group(1)
        return ycode
    else:
        return None


class DpipblockServer:
    def dpfhq_port_management_add(self, ip: str, time_str: str) -> str:
        headers = dpfhq_login('admin', 'Khxxb2421!@')
        if headers is not None:
            # 将时间字符串转换为秒数
            time_seconds = convert_time_to_seconds(time_str)
            
            params = {
                'to_add': '端口封禁?Default?1?'+ip+'?'+ip+'?32?'+time_seconds+'?2?1',
                'del_all': None
            }
            url = 'https://10.138.36.249:8889/func/web_main/submit/maf/maf_addrfilter/maf_cidr_v4_wblist'
            main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
            response = main_url_html.text
            dpfhq_logout(headers)
            if response.__contains__("HiddenSubWin"):
                return f"({ip})端口封禁成功！封禁时长：{time_str}（{time_seconds}秒）"
            else:
                return f"({ip})端口封禁失败！"
        else:
            return f"({ip})登录失败，无法执行封禁操作！"
    
    
    def dpfhq_port_management_delete(self, ip: str) -> str:
        headers = dpfhq_login('admin', 'Khxxb2421!@')
        if headers is not None:
            valueId = dpfhq_port_management_getValueId(ip, headers)
            if valueId is not None:
                params = {
                    'to_delete': valueId + '?Default?1?'+ip+'?'+ip+'?32?180?2?1',
                    'del_all': None
                }
                url = 'https://10.138.36.249:8889/func/web_main/submit/maf/maf_addrfilter/maf_cidr_v4_wblist'
                main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
                response = main_url_html.text
                dpfhq_logout(headers)
                if response.__contains__("HiddenSubWin"):
                    return "(" + ip + ")端口解禁成功！"
                else:
                    return "(" + ip + ")端口解禁失败！"
            else:
                dpfhq_logout(headers)
                return f"({ip})未找到对应的封禁记录！"
        else:
            return f"({ip})登录失败，无法执行解禁操作！"


async def serve() -> None:
    """运行IP管理MCP服务"""
    server = Server("mcp-dpipblock")
    tdpipblock_server = DpipblockServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available dpipblock tools."""
        return [
            Tool(
                name=DpipblockTools.PORT_ADD.value,
                description="在防火墙层面封禁IP地址",
                inputSchema= {
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address to be blocked at the port level, e.g., '192.168.1.1'",
                        },
                        "time": {
                            "type": "string",
                            "description": "Time of sequestration. Supports formats: '永久'(permanent), '1分钟'/'1min'/'1m', '1小时'/'1hour'/'1h', '1天'/'1day'/'1d', '1周'/'1week'/'1w', '1月'/'1month', '1年'/'1year'/'1y', or pure number (seconds)",
                        }
                    },
                    "required": ["ip","time"]
                },
            ),
            Tool(
                name=DpipblockTools.PORT_DELETE.value,
                description="在防火墙层面解封IP地址",
                inputSchema = {
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address to be unblocked at the port level, e.g., '192.168.1.1'",
                        }
                    },
                    "required": ["ip"]
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            match name:
                case DpipblockTools.PORT_ADD.value:
                    if not all(
                        k in arguments
                        for k in ["ip", "time"]
                    ):
                        raise ValueError("Missing required arguments")
                    
                    result = tdpipblock_server.dpfhq_port_management_add(
                        arguments["ip"],
                        arguments["time"],
                        )

                case DpipblockTools.PORT_DELETE.value:
                    ip = arguments.get("ip")
                    if not ip:
                        raise ValueError("Missing required argument: ip")
                    
                    result = tdpipblock_server.dpfhq_port_management_delete(ip)
               
                case _:
                    raise ValueError(f"Unknown tool: {name}")
            return [TextContent(type="text", text=result)]

        except Exception as e:
            raise ValueError(f"Error processing mcp-server-dpipblock query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


