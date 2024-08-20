import requests
import os
import json
import argparse
import time

# Giant配置
LOGIN_URL = "https://ridelife.giant.com.cn/index.php/api/login"
UPLOAD_URL = "https://ridelife.giant.com.cn/index.php/api/upload_fit"
DAILY_SIGN_URL = "https://opo.giant.com.cn/opo/index.php/day_pic/do_app_pic"

# 设置变量
DEVICE = "bike_computer"
BRAND = "garmin"
FOLDER_PATH = "FIT_OUT"

# 指定 boundary
BOUNDARY = "----WebKitFormBoundaryreNAGwfDuBI8rK4S"


def upload_to_giant(username, password):
    # 创建一个会话
    session = requests.Session()
    token = ""
    userID = ""

    # 登录
    login_headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
    login_data = {"username": username, "password": password}
    login_response = session.post(LOGIN_URL, headers=login_headers, data=login_data)
    login_json = login_response.json()
    if login_json["status"] == 1:
        print("登录成功，已获取 Token")
        token = login_json["user_token"]
        userID = login_json["user"]["userId"]
    else:
        print(f"登录失败，状态码: {login_response.status_code}")
        print(f"响应内容: {login_response.text}")

    # 签到
    daily_sign_data = {"type": "1", "user_id": userID}
    daily_sign_response = session.post(
        DAILY_SIGN_URL, headers=login_headers, data=daily_sign_data
    )
    daily_sign_json = daily_sign_response.json()
    print(daily_sign_json)

    # 上传
    upload_headers = {"Content-Type": f"multipart/form-data; boundary={BOUNDARY}"}
    for file_name in os.listdir(FOLDER_PATH):
        if file_name.endswith(".fit"):
            file_path = os.path.join(FOLDER_PATH, file_name)
        with open(file_path, "rb") as file:
            file_data = file.read()
        form_data = (
            (
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="token"\r\n\r\n'
                f"{token}\r\n"
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="device"\r\n\r\n'
                f"{DEVICE}\r\n"
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="brand"\r\n\r\n'
                f"{BRAND}\r\n"
                f"--{BOUNDARY}\r\n"
                f'Content-Disposition: form-data; name="files[]"; filename="{file_name}"\r\n'
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
    parser.add_argument("username", nargs="?", help="input giant username")
    parser.add_argument("password", nargs="?", help="input giant password")
    options = parser.parse_args()

    username = options.username
    password = options.password

    upload_to_giant(username, password)
