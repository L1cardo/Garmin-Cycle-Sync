import requests
import os
import json
import argparse
import time

# IGP配置
LOGIN_URL = "https://my.igpsport.com/Auth/Login"
UPLOAD_URL = "https://my.igpsport.com/upload/FileUpload"

# 设置变量
FOLDER_PATH = "FIT_OUT"

# 指定 boundary
BOUNDARY = "----WebKitFormBoundarytANDuaLBsBWBpNJu"


def upload_to_igp(username, password):
    # 创建一个会话
    session = requests.Session()

    login_headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
    upload_headers = {"Content-Type": f"multipart/form-data; boundary={BOUNDARY}"}
    login_data = {
        "username": username,
        "password": password,
    }
    login_response = session.post(LOGIN_URL, headers=login_headers, data=login_data)
    login_json = login_response.json()
    if login_json["Code"] == 0:
        print("登录成功")
    else:
        print(f"登录失败，状态码: {login_response.status_code}")
        print(f"响应内容: {login_response.text}")

    # 使用相同的会话上传 FIT 文件，携带登录所获得的 Cookie
    for file_name in os.listdir(FOLDER_PATH):
        if file_name.endswith(".fit"):
            file_path = os.path.join(FOLDER_PATH, file_name)
        with open(file_path, "rb") as file:
            file_data = file.read()
        form_data = (
            (
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
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

    parser.add_argument("username", nargs="?", help="input igp username")
    parser.add_argument("password", nargs="?", help="input igp password")
    options = parser.parse_args()

    username = options.username
    password = options.password

    upload_to_igp(username, password)
