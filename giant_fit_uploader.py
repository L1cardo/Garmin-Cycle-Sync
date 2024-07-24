import requests
import os
import json
import argparse

# Giant配置
LOGIN_URL = "https://ridelife.giant.com.cn/index.php/api/login"
UPLOAD_URL = "https://ridelife.giant.com.cn/index.php/api/upload_fit"

# 设置变量
DEVICE = "bike_computer"
BRAND = "garmin"
FOLDER_PATH = "FIT_OUT"

# 指定 boundary
BOUNDARY = "----WebKitFormBoundaryreNAGwfDuBI8rK4S"

def get_token(username, password):
    login_data = {
        "username": username,
        "password": password
    }
    login_headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
    }

    login_response = requests.post(LOGIN_URL, headers=login_headers, data=login_data)

    login_json = login_response.json()
    if login_json["status"] == 1:
        print("登录成功，已获取 Token")
        return login_json["user_token"]
    else:
        print("登录失败")
        exit()

def upload_fit_files_to_giant(username, password):
    token = get_token(username, password)
    form_data = (
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="token"\r\n\r\n'
        f'{token}\r\n'
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="device"\r\n\r\n'
        f'{DEVICE}\r\n'
        f'--{BOUNDARY}\r\n'
        f'Content-Disposition: form-data; name="brand"\r\n\r\n'
        f'{BRAND}\r\n'
    )

    for file_name in os.listdir(FOLDER_PATH):
        if file_name.endswith(".fit"):
            file_path = os.path.join(FOLDER_PATH, file_name)
        with open(file_path, 'rb') as file:
            file_data = file.read()
        form_data += (
            f'--{BOUNDARY}\r\n'
            f'Content-Disposition: form-data; name="files[]"; filename="{file_name}"\r\n'
            f'Content-Type: "application/octet-stream"\r\n\r\n'
            f'{file_data}\r\n'
            f'--{BOUNDARY}\r\n'
        )
    upload_headers = {
        "Content-Type": f"multipart/form-data; boundary={BOUNDARY}"
    }

    upload_response = requests.post(UPLOAD_URL, headers=upload_headers, data=form_data.encode('utf-8'))

    print(f"Status Code: {upload_response.status_code}")

    try:
        response_json = upload_response.json()
        if 'msg' in response_json:
            print(f"Response: {json.dumps(response_json, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print("Response is not valid JSON")
        print(f"Raw response: {upload_response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username", nargs="?", help="input giant username")
    parser.add_argument("password", nargs="?", help="input giant password")
    options = parser.parse_args()

    username = options.username
    password = options.password

    upload_fit_files_to_giant(username, password)