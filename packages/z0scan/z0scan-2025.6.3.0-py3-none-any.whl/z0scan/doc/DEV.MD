# Scanner 编写

## 命名

插件名称按照以下命名规则命名：
```
漏洞类型(简写) + 指纹 + 简述
```
漏洞类型分类与简写形式见`api/VulType`部分


## 内置模块

### api:
| 名称 | 描述 | 使用 | 必选/可选 |
| --------- | -------- | --------- | -------- | 
| generateResponse | 用于报告中响应体的生成 | generateResponse(r) # r=request.get(…) | 必选 |
| random_num | 生成随机数 | / | 可选 |
| random_str | 生成随机字符串 | / | 可选 |
| VulType | 对漏洞类型的选定 | 见api/VulType | 必选 |
| Type | 对扫描类型的选定 | 见api/Type | 必选 |
| PluginBase | 被继承以获取关键数据 | class Z0SCAN(PluginBase) | 必选 |
| conf | 储存一些命令行参数值 | 主要使用level，见api/conf.level | 必选 |
| PLACE | 对漏洞注入点（请求中的可控点）的选定 | 见api/PLACE | 必选 |

- api/VulType:

| 名称 | 描述 | (插件命名)简写 |
| --------- | -------- | -------- |
| CMD_INNJECTION | 命令注入漏洞 | cmdi |
| CODE_INJECTION | 代码注入漏洞 | codei |
| XSS | XSS跨站脚本攻击 | xss |
| SQLI | SQL注入漏洞 | sqli |
| TRAVERSAL | 遍历漏洞 | trave |
| XXE | XML外部实体注入 | xxe |
| SSRF | 服务器端请求伪造 | ssrf |
| CSRF | CSRF | csrf |
| REDIRECT | 重定向漏洞 | redirect |
| WEAK_PASSWORD | 弱口令 | weakpwd |
| CRLF | 换行注入 | crlf |
| SENSITIVE | 敏感信息泄露漏洞 | sensi |
| SSTI | 服务器端模板注入 | ssti |
| UNAUTH | 未授权访问 | unauth |
| FILEUPLOAD | 文件上传 | upload |
| CORS | CORS漏洞 | cors |
| OTHER | 其它漏洞 | other |

- api/Type :

| 名称 | 描述 |
| --------- | -------- |
| ANALYZE | 被动分析发现 |
| REQUEST | 主动请求发现 |

- api/conf.level :

扫描深度（反映请求量）
| 值 | 描述 |
| --------- | -------- |
| 0 | 纯被动分析模式，不做任何请求 |
| 1 | 最低请求量的扫描，最低的业务影响 |
| 2 | 中等请求量的扫描，Payload多为通用Top5 |
| 3 | 大量请求扫描，Payload覆盖面更广 |

- api/conf.risk :

需要扫描的漏洞危害程度
| 值 | 描述 |
| --------- | -------- |
| -1 | 难以利用的极低危常见漏洞 |
| 0 | 可能产生1~3级危害的辅助性信息 |
| 1 | 低危漏洞 |
| 2 | 中危漏洞 |
| 3 | 高危漏洞 |

- api/PLACE :

| 名称 | 描述 |
| --------- | -------- |
| PARAM | URL后参数部分 |
| DATA | 在BODY中传递的参数 |
| COOKIE | COOKIE中传递的参数 |
| URL | 伪静态参数 |
| NORMAL_DATA | 常规POST传参格式中的参数 |
| JSON_DATA | JSON格式中的参数 |
| XML_DATA | XML格式中的参数 |
| MULTIPART_DATA | MULTIPART格式中的参数 |
| ARRAY_LIKE_DATA | ARRAY_LIKE格式中的参数 |
| SOAP_DATA | SOAP_DATA格式中的参数 |


## 解析出的数据
注：继承PluginBase后读取

- self.fingerprints :

| 名称 | 类型 | 描述 |
| --------- | ------- | -------- | 
| os | dict | OS系统指纹 |
| programing | dict | 项目类型 |
| waf | str | WAF名称（未检测到WAF时为None） |
对于`os、webserver、programing`：
```
>> print(self.fingerprints.programing)
{"PHP" : "1.9.6"} # 名称 : 版本信息
```

- self.requests :

| 名称 | 类型 | 描述 | 示例 |
| --------- | -------- | --------- | ------- |
| url | str  | 完整的URL（包含GET参数） | https://www.example.com:443/a/file.php?id=1 |
| suffix  | str | 文件后缀 | .php |
| scheme | str | 请求协议 | http |
| port | int | 服务端口 | 8888 |
| host | str | 域名（不包括端口）| www.myscantest.com |
| netloc | str | 包含协议与端口信息的域名 | https://www.example.com:443 |
| raw  | str  | 原始的请求包 | / |
| method | str |  请求方法  | GET |
| headers   | dict  |  请求头字典  | / |
| cookies | dict | COOKIE | / |
| params | dict |  在URL中包含的参数  | {'id': '1'} |
| post_hint | str  | POST请求包类型 | / |
| datas | dict |  POST数据  | / |
| data | str | 原始请求头 | / |

注: 仅常规解析，datas、params均允许直接requests构造请求
如需解析伪静态及xml等格式请求中的参数，见self.generateItemdatas()

- self.response :

| 名称 | 类型 | 描述  | 示例 |
| --------- | -------- | -------- | ------- |
| status | int | 返回状态码 | 200 |
| content | byte | 返回字节类型 | /  |
| headers | dict | 请求头  | / |
| raw | str | 原始的返回包 | / |
| text | str  | 返回的文本 | / |

- self.generateItemdatas() :

generateItemdatas()会将参数名、参数值及其所处的可控点整理后返回
注意: 它会额外地解析出伪静态及xml等包含的参数，
并按照用户要求不将cookie参数作为解析对象，
以达到不对cookie扫描检测的目的。
```
>> iterdatas = self.generateItemdatas()
>> print(iterdatas)
[
    ["id", "1", "URL"],
    ["username", "admin", "DATA"],
]
```

- self.insertPayload({"key": k, "value": v, "position": position, "payload": _payload}) :

令参数名为key，参数值为value（value为可选值），并向参数值后添加payload
最终返回其对应可控点修改后的数据
建议配合self.generateItemdatas()使用
```
>> datas = self.insertPayload({"key": "username", "value": "admin", "position": "DATA", "payload": "'--+"})
>> print(datas)
{"username": "admin'--+", "passwd": "admin"}
>> r = request.get(url, data=datas)
```

- self.req(position, payload) :

payload为对应可控点修改后的整体数据，可以为self.insertPayload的返回
需配合self.generateItemdatas()使用
```
>> datas = {"username": "admin'--+", "passwd": "admin"}
>> r = self.req("DATA", datas)
>> print(r)
… # r为request的返回
```


## 示范

```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# w8ay 2020/5/10
# JiuZero 2025/3/13

from data.rule.sqli_error import rules
from api import generateResponse, random_num, random_str, VulType, Type, PluginBase, conf, logger
from lib.helper.helper_sensitive import sensitive_page_error_message_check
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

class Z0SCAN(PluginBase):
    name = "sqli-error" # 插件名
    desc = 'SQL Error Finder' # 描述
    version = "2025.3.13" # 版本（最后更新日期）
    risk = 2 # 危害等级
        
    def audit(self):
        if not self.fingerprints.waf and 2 in conf.risk and conf.level != 0:
            _payloads = [
                ## 宽字节
                r'鎈\'"\(',
                ## 通用报错
                r';)\\\'\\"',
                r'\' oRdeR bY 500 ',
                r';`)',
                r'\\', 
                r"%%2727", 
                r"%25%27", 
                r"%60", 
                r"%5C",
            ]
            if conf.level == 3: 
                _payloads += [
                ## 强制报错
                # MySQL
                r'\' AND 0xG1#',
                # PostgreSQL  
                r"' AND 'a' ~ 'b\[' -- ",
                # MSSQL
                r"; RAISERROR('Error generated', 16, 1) -- ", 
                # Oracle
                r"' UNION SELECT XMLType('<invalid><xml>') FROM dual -- ",  
                # SQLite
                r"' UNION SELECT SUBSTR('o', -1, 1) -- ",
                ]
    
            iterdatas = self.generateItemdatas()
            # 内置的线程并发
            with ThreadPoolExecutor(max_workers=None) as executor:
                futures = [
                    executor.submit(self.process, _, _payloads) for _ in iterdatas
                ]
                try:
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as task_e:
                            logger.error(f"Task failed: {task_e}", origin=self.name)
                except KeyboardInterrupt:
                    executor.shutdown(wait=False)
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", origin=self.name)
                    executor.shutdown(wait=False)
    
    def Get_sql_errors(self):
        sql_errors = []
        for database, re_strings in rules.items():
            for re_string in re_strings:
                sql_errors.append((re.compile(re_string, re.IGNORECASE), database))
        return sql_errors
    
    def process(self, _, _payloads):
        k, v, position = _
        for _payload in _payloads:
            payload = self.insertPayload({
                "key": k, 
                "value": v, 
                "position": position, 
                "payload": _payload
                })
            r = self.req(position, payload)
            if not r:
                continue
            html = r.text
            for sql_regex, dbms_type in self.Get_sql_errors():
                match = sql_regex.search(html)
                if match:
                    # 生成报告
                    result = self.generate_result()
                    result.main({
                        "type": Type.REQUEST, # 扫描类型
                        "url": self.requests.url, # 漏洞URL
                        "vultype": VulType.SQLI, # 漏洞类型
                        "show": { # 你希望向命令行展示的信息
                            "Position": f"{position} > {k}", # 建议键名首字母大写
                            "Payload": payload, 
                            "Msg": "DBMS_TYPE Maybe {}; Match {}".format(dbms_type, match.group())
                            }
                        })
                    # 验证步骤(可以添加多个过程，如二次验证)
                    result.step("Request1", {
                        "request": r.reqinfo, 
                        "response": generateResponse(r), 
                        "desc": "Dbms Maybe {}; Match {}".format(dbms_type, match.group())
                        })
                    self.success(result)
                    return True
            message_lists = sensitive_page_error_message_check(html)
            if message_lists:
                result = self.generate_result()
                result.main({
                    "type": Type.REQUEST, 
                    "url": self.requests.url, 
                    "vultype": VulType.SQLI, 
                    "show": {
                        "Position": f"{position} > {k}", 
                        "Payload": payload, 
                        "Msg": "Receive Error Msg {}".format(repr(message_lists))
                        }
                    })
                result.step("Request1", { # 步骤标题
                    "request": r.reqinfo, # 请求体
                    "response": generateResponse(r), # 响应体(由generateResponse生成)
                    "desc": "Receive Error Msg {}".format(repr(message_lists)) # 步骤的关键信息
                    })
                self.success(result)
                break
    
```