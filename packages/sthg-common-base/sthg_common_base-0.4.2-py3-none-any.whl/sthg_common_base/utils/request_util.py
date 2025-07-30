"""
@Author  ：duomei
@File    ：request_util.py
@Time    ：2025/4/28 16:07
"""
import json

import requests
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout, TooManyRedirects, URLRequired, InvalidURL, \
    InvalidHeader, InvalidProxyURL

from sthg_common_base import BaseResponse, ResponseEnum, format_exception_msg, access_log


class RequestUtil:

    @staticmethod
    @access_log()
    def get(url: str, headers=None, params=None, encoding=None, timeout=30):
        """
        同步get
        :param url: 请求的URL
        :param headers: 请求头
        :param timeout: 超时时间，默认为10秒
        :param params: URL参数
        :param encoding: 编码方式
        :return: 解析后的JSON响应
        """
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            if encoding:
                response.encoding = encoding
            text = response.text
            return BaseResponse(data=json.loads(text), resEnum=ResponseEnum.OK,msg=f"请地址url:{url}")
        except ReadTimeout as e:
            return BaseResponse(resEnum=ResponseEnum.RequestTimeout, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except TooManyRedirects as e:
            return BaseResponse(resEnum=ResponseEnum.Too_Many_Redirects, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except URLRequired as e:
            return BaseResponse(resEnum=ResponseEnum.InvalidRequest, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except InvalidURL as e:
            return BaseResponse(resEnum=ResponseEnum.InvalidURI, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except InvalidHeader as e:
            return BaseResponse(resEnum=ResponseEnum.Invalid_Header, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except InvalidProxyURL as e:
            return BaseResponse(resEnum=ResponseEnum.Invalid_Proxy_URL, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except ConnectionError as e:
            return BaseResponse(resEnum=ResponseEnum.ConnectionError, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except ConnectTimeout as e:
            return BaseResponse(resEnum=ResponseEnum.ConnectionTimeout, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except Exception as e:
            return BaseResponse(resEnum=ResponseEnum.InternalError, msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))

    @staticmethod
    @access_log()
    def post(url: str, headers=None, json_data=None, encoding=None, timeout=30):
        """
        同步post
        :param url: 请求的URL
        :param headers: 请求头
        :param timeout: 超时时间，默认为10秒
        :param json_data: 要发送的JSON数据
        :param encoding: 编码方式
        :return: 解析后的JSON响应
        """
        try:
            result = requests.post(url, headers=headers, json=json_data, timeout=timeout)
            if encoding:
                result.encoding = encoding
            text = result.text
            return BaseResponse(data=json.loads(text), resEnum=ResponseEnum.OK,msg=f"请地址url:{url}")
        except ReadTimeout as e:
            return BaseResponse(resEnum=ResponseEnum.RequestTimeout,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except TooManyRedirects as e:
            return BaseResponse(resEnum=ResponseEnum.Too_Many_Redirects,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except URLRequired as e:
            return BaseResponse(resEnum=ResponseEnum.InvalidRequest,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except InvalidURL as e:
            return BaseResponse(resEnum=ResponseEnum.InvalidURI,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except InvalidHeader as e:
            return BaseResponse(resEnum=ResponseEnum.Invalid_Header,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except InvalidProxyURL as e:
            return BaseResponse(resEnum=ResponseEnum.Invalid_Proxy_URL,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except ConnectionError as e:
            return BaseResponse(resEnum=ResponseEnum.ConnectionError,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except ConnectTimeout as e:
            return BaseResponse(resEnum=ResponseEnum.ConnectionTimeout,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))
        except Exception as e:
            return BaseResponse(resEnum=ResponseEnum.InternalError,msg=f"请地址url:{url}",exceptionStack = format_exception_msg(e))


if __name__ == "__main__":
    # 测试http_get方法 - 成功案例
    print("测试http_get - 成功案例:")
    get_result = RequestUtil.http_get(
        url="https://httpbin.org/get",
        params={"test": "value"},
        headers={"User-Agent": "TestClient"}
    )
    print(f"状态码: {get_result.code}")
    print(f"业务消息: {get_result.busiMsg}")
    if get_result.code == ResponseEnum.OK.getHttpCode:
        print(f"响应数据: {get_result.data}")
        print(f"请求ID: {get_result.requestId}")
    else:
        print(f"错误信息: {get_result.exceptionStack}")

    # 测试http_get方法 - 超时案例
    print("\n测试http_get - 超时案例:")
    timeout_result = RequestUtil.http_get(
        url="https://httpbin.org/delay/5",  # 这个端点会延迟5秒响应
        timeout=1  # 设置1秒超时
    )
    print(f"状态码: {timeout_result.code}")
    print(f"业务消息: {timeout_result.busiMsg}")
    print(f"错误堆栈: {timeout_result.exceptionStack}")

    # 测试http_post方法 - 成功案例
    print("\n测试http_post - 成功案例:")
    post_data = {"key": "value", "number": 42}
    post_result = RequestUtil.http_post(
        url="https://httpbin.org/post",
        json_data=post_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"状态码: {post_result.code}")
    print(f"业务消息: {post_result.busiMsg}")
    if post_result.code == ResponseEnum.OK.getHttpCode:
        print(f"响应数据: {post_result.data}")
        print(f"请求ID: {post_result.requestId}")
    else:
        print(f"错误信息: {post_result.exceptionStack}")

    # 测试http_post方法 - 错误URL案例
    print("\n测试http_post - 错误URL案例:")
    error_result = RequestUtil.http_post(
        url="https://invalid-domain-xyz.example/api",
        json_data={"test": "data"}
    )
    print(f"状态码: {error_result.code}")
    print(f"业务消息: {error_result.busiMsg}")
    print(f"错误堆栈: {error_result.exceptionStack}")

    # 测试http_post方法 - 无效JSON响应
    print("\n测试http_post - 无效JSON响应:")
    invalid_json_result = RequestUtil.http_post(
        url="https://httpbin.org/html",  # 返回HTML内容而不是JSON
        headers={"Accept": "application/json"}  # 故意要求JSON
    )
    print(f"状态码: {invalid_json_result.code}")
    print(f"业务消息: {invalid_json_result.busiMsg}")
    print(f"错误堆栈: {invalid_json_result.exceptionStack}")