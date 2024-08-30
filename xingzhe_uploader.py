import requests
import os
import json
import argparse
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import hashlib

# Xingzhe配置
LOGIN_URL = "https://www.imxingzhe.com/api/v1/user/login/"
UPLOAD_URL = "https://www.imxingzhe.com/api/v1/fit/upload/"

# 设置变量
FOLDER_PATH = "FIT_OUT"

# 指定 boundary
BOUNDARY = "----WebKitFormBoundaryrGuwAFg837SqSW98"


def upload_to_xingzhe(account, password):
    # 创建一个会话
    session = requests.Session()

    # 将密码转为 base64
    public_key = "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDmuQkBbijudDAJgfffDeeIButq\nWHZvUwcRuvWdg89393FSdz3IJUHc0rgI/S3WuU8N0VePJLmVAZtCOK4qe4FY/eKm\nWpJmn7JfXB4HTMWjPVoyRZmSYjW4L8GrWmh51Qj7DwpTADadF3aq04o+s1b8LXJa\n8r6+TIqqL5WUHtRqmQIDAQAB\n-----END PUBLIC KEY-----\n"
    rsa = RSA.importKey(public_key)
    cipher = PKCS1_v1_5.new(rsa)
    encrypted_password = base64.b64encode(cipher.encrypt(password.encode())).decode()

    login_headers = {"Content-Type": "application/json; charset=UTF-8"}
    upload_headers = {"Content-Type": f"multipart/form-data; boundary={BOUNDARY}"}
    login_data = {"account": account, "password": encrypted_password}

    login_response = session.post(
        LOGIN_URL, headers=login_headers, data=json.dumps(login_data)
    )
    login_json = login_response.json()
    if login_json["code"] == 0:
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
            md5_hash = hashlib.md5(file_data).hexdigest()
        form_data = (
            (
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="fit_filename"\r\n\r\n'
                f'{file_name}'
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="md5"\r\n\r\n'
                f'{md5_hash}\r\n'
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="name"\r\n\r\n'
                f'{file_name.removesuffix(".fit")}\r\n'
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="sport"\r\n\r\n'
                f'{3}\r\n'
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="fit_file"; filename="{file_name}"\r\n'
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
                f"上传信息：{file_name}, {response_json}, Status Code: {upload_response.status_code}"
            )
        except json.JSONDecodeError:
            print("Response is not valid JSON")
            print(f"Raw response: {upload_response.text}")

        time.sleep(1)  # 每次请求之间等待 1 秒


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("account", nargs="?", help="input xingzhe account")
    parser.add_argument("password", nargs="?", help="input xingzhe password")
    options = parser.parse_args()

    account = options.account
    password = options.password

    upload_to_xingzhe(account, password)
