import requests
import os
import json
import argparse
import re
import hashlib
import time

# Onelap配置
LOGIN_URL = "https://www.onelap.cn/api/login"
ANALYSIS_URL = "http://u.onelap.cn/analysis"
UPLOAD_URL = "http://u.onelap.cn/upload/fit"

# 设置变量
FOLDER_PATH = "FIT_OUT"

# 指定 boundary
BOUNDARY = "---WebKitFormBoundaryNBbAxaxMrDmeCqdn"


def upload_to_onelap(account, password):
    # 创建一个会话
    session = requests.Session()
    token = ""

    login_headers = {"Content-Type": "application/json;charset=UTF-8"}
    upload_headers = {"Content-Type": f"multipart/form-data; boundary={BOUNDARY}"}
    login_data = {
        "account": account,
        "password": hashlib.md5(password.encode()).hexdigest(),
    }
    login_response = session.post(
        LOGIN_URL, headers=login_headers, data=json.dumps(login_data)
    )
    if login_response.status_code == 200:
        print("登录成功")
    else:
        print(f"登录失败，状态码: {login_response.status_code}")
        print(f"响应内容: {login_response.text}")

    # 使用相同的会话发送 GET 请求到分析页面, 获取上传所需的 Cookie 和 Token
    analysis_response = session.get(ANALYSIS_URL)
    if analysis_response.status_code == 200:
        # 提取 _token
        html_content = analysis_response.text
        token_match = re.search(r'<meta name="_token" content="([^"]+)"', html_content)

        if token_match:
            token = token_match.group(1)
            print(f"提取的 _token 值: {token}")
        else:
            print("未找到 _token")
    else:
        print(f"访问分析页面失败，状态码: {analysis_response.status_code}")
        print(f"响应内容: {analysis_response.text}")

    for file_name in os.listdir(FOLDER_PATH):
        if file_name.endswith(".fit"):
            file_path = os.path.join(FOLDER_PATH, file_name)
        with open(file_path, "rb") as file:
            file_data = file.read()
        form_data = (
            (
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="_token"\r\n\r\n'
                f"{token}\r\n"
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="jilu"; filename="{file_name}"\r\n'
                f"Content-Type: application/octet-stream\r\n\r\n"
            ).encode("utf-8")
            + file_data
            + f"\r\n--{BOUNDARY}--\r\n".encode("utf-8")
        )

        upload_response = session.post(
            UPLOAD_URL, headers=upload_headers, data=form_data
        )

        try:
            response_json = upload_response.json()
            print(
                f"{file_name}, {response_json}, Status Code: {upload_response.status_code}"
            )
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            print(f"Raw response: {upload_response.text}")

        time.sleep(1)  # 每次请求之间等待 1 秒


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("account", nargs="?", help="input onelap account")
    parser.add_argument("password", nargs="?", help="input onelap password")
    options = parser.parse_args()

    account = options.account
    password = options.password

    upload_to_onelap(account, password)
